"""Analysis model — AI body composition estimates per photo set."""
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, Float, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    photo_set_id: Mapped[int] = mapped_column(Integer, index=True)
    body_fat_pct: Mapped[float] = mapped_column(Float, nullable=False)
    muscle_mass_kg: Mapped[float] = mapped_column(Float, nullable=False)
    lean_mass_kg: Mapped[float] = mapped_column(Float, nullable=False)
    posture_score: Mapped[float] = mapped_column(Float, nullable=False)  # 0-100
    weak_muscles: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    fat_distribution: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    notes: Mapped[str] = mapped_column(String(512), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="analyses")
