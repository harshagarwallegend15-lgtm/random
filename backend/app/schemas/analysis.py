"""Analysis schemas."""
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class AnalysisOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    photo_set_id: int
    body_fat_pct: float
    muscle_mass_kg: float
    lean_mass_kg: float
    posture_score: float
    weak_muscles: list
    fat_distribution: dict
    notes: str | None
    created_at: datetime
