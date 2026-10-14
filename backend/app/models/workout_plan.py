"""WorkoutPlan model — exercises per day within a roadmap week."""
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class WorkoutPlan(Base):
    __tablename__ = "workout_plans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    day: Mapped[int] = mapped_column(Integer, nullable=False)  # 1-7
    title: Mapped[str] = mapped_column(String(64), nullable=False, default="")
    exercises: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    roadmap: Mapped["Roadmap"] = relationship(back_populates="workout_plans")
