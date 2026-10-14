"""Weekly re-analyze: upload new photos, run analysis, adjust plan, predict target date."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import Analysis, Photo, User
from app.schemas import AnalysisOut
from app.services import body_metrics, storage, vision

router = APIRouter(prefix="/reanalyze", tags=["reanalyze"])
log = logging.getLogger(__name__)

_MAX_BYTES = settings.max_upload_mb * 1024 * 1024


@router.post("/{user_id}", response_model=AnalysisOut, status_code=201)
async def reanalyze(
    user_id: int = Form(...),
    front: UploadFile = File(...),
    side: UploadFile = File(...),
    back: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    uploads = {"front": front, "side": side, "back": back}
    file_bytes: dict[str, bytes] = {}
    for angle, upload in uploads.items():
        data = await upload.read()
        if len(data) > _MAX_BYTES:
            raise HTTPException(
                status_code=413,
                detail=f"{angle} photo exceeds {settings.max_upload_mb} MB limit",
            )
        file_bytes[angle] = data

    landmarks = vision.extract_set(file_bytes["front"], file_bytes["side"], file_bytes["back"])

    set_id = uuid.uuid4().int >> 96
    for angle, data in file_bytes.items():
        url, public_id = storage.upload_image(data, user_id, angle)
        db.add(Photo(
            user_id=user_id,
            angle=angle,
            cloudinary_url=url,
            cloudinary_public_id=public_id,
            set_id=set_id,
            landmarks=landmarks.get(angle),
        ))

    previous = db.execute(
        select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.id.desc()).limit(1)
    ).scalar_one_or_none()

    result = body_metrics.analyse(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        landmarks=landmarks,
    )

    delta = body_metrics.delta_vs_previous(
        result,
        {
            "muscle_mass_kg": previous.muscle_mass_kg,
            "body_fat_pct": previous.body_fat_pct,
            "posture_score": previous.posture_score,
        } if previous else None,
    )

    notes = result["notes"]
    if not delta["first_analysis"]:
        if delta["fat_change_pct"] < -0.3:
            notes += f" Fat ↓{abs(delta['fat_change_pct']):.1f}% — plan is working."
        if delta["muscle_change_kg"] > 0.2:
            notes += f" Muscle ↑{delta['muscle_change_kg']:.1f}kg — keep it up."
        if delta["posture_change"] > 2:
            notes += f" Posture improved by {delta['posture_change']:.1f} pts."

    analysis = Analysis(
        user_id=user_id,
        photo_set_id=set_id,
        body_fat_pct=result["body_fat_pct"],
        muscle_mass_kg=result["muscle_mass_kg"],
        lean_mass_kg=result["lean_mass_kg"],
        posture_score=result["posture_score"],
        weak_muscles=result["weak_muscles"],
        fat_distribution=result["fat_distribution"],
        notes=notes,
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)
    log.info("Re-analysis %s for user %s: bf=%.1f muscle=%.1f",
             analysis.id, user_id, result["body_fat_pct"], result["muscle_mass_kg"])
    return analysis
