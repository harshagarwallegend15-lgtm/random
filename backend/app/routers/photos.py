"""Photo upload + AI analysis trigger."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Analysis, Photo, User
from app.schemas import AnalysisOut
from app.services import body_metrics, storage, vision

log = logging.getLogger(__name__)

router = APIRouter(prefix="/photos", tags=["photos"])

_MAX_BYTES = settings.max_upload_mb * 1024 * 1024


@router.post("/upload", response_model=AnalysisOut, status_code=201)
async def upload_photos(
    user_id: int = Form(...),
    front: UploadFile = File(...),
    side: UploadFile = File(...),
    back: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """Upload 3 photos (front/side/back) for a user. Triggers AI body analysis."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    files = {"front": front, "side": side, "back": back}
    file_bytes: dict[str, bytes] = {}
    for angle, upload in files.items():
        data = await upload.read()
        if len(data) > _MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"{angle} photo exceeds {settings.max_upload_mb} MB limit",
            )
        file_bytes[angle] = data

    # 1) Run vision pipeline
    landmarks = vision.extract_set(file_bytes["front"], file_bytes["side"], file_bytes["back"])

    # 2) Upload to storage (Cloudinary or local fallback)
    set_id = uuid.uuid4().int >> 96  # short id grouping 3 photos
    photo_rows: list[Photo] = []
    for angle, data in file_bytes.items():
        url, public_id = storage.upload_image(data, user_id, angle)
        photo_rows.append(Photo(
            user_id=user_id,
            angle=angle,
            cloudinary_url=url,
            cloudinary_public_id=public_id,
            set_id=set_id,
            landmarks=landmarks.get(angle),
        ))
    db.add_all(photo_rows)

    # 3) Body composition analysis
    result = body_metrics.analyse(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        landmarks=landmarks,
    )

    # 4) Persist analysis
    analysis = Analysis(
        user_id=user_id,
        photo_set_id=set_id,
        body_fat_pct=result["body_fat_pct"],
        muscle_mass_kg=result["muscle_mass_kg"],
        lean_mass_kg=result["lean_mass_kg"],
        posture_score=result["posture_score"],
        weak_muscles=result["weak_muscles"],
        fat_distribution=result["fat_distribution"],
        notes=result["notes"],
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    log.info("Analysis %s for user %s: bf=%.1f posture=%.1f",
             analysis.id, user_id, result["body_fat_pct"], result["posture_score"])
    return analysis
