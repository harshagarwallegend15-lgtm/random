"""Analysis read routes."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Analysis
from app.schemas import AnalysisOut

router = APIRouter(prefix="/analysis", tags=["analysis"])


@router.get("/{user_id}/latest", response_model=AnalysisOut)
def latest_analysis(user_id: int, db: Session = Depends(get_db)):
    stmt = select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.id.desc()).limit(1)
    analysis = db.execute(stmt).scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="No analysis yet — upload photos first")
    return analysis


@router.get("/{user_id}/history", response_model=list[AnalysisOut])
def analysis_history(user_id: int, db: Session = Depends(get_db)):
    stmt = select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.id.asc())
    return list(db.execute(stmt).scalars().all())
