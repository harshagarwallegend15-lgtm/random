"""User profile model."""
from datetime import datetime
from sqlalchemy import String, Integer, Float, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    height_cm: Mapped[float] = mapped_column(Float, nullable=False)
    weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(16), nullable=False)  # male|female|other
    target_weight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    budget_inr: Mapped[float] = mapped_column(Float, nullable=False, default=3000.0)
    city: Mapped[str] = mapped_column(String(64), nullable=False)
    vegetarian: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    gym_available: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    schedule: Mapped[str] = mapped_column(String(256), nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    photos: Mapped[list["Photo"]] = relationship(back_populates="user", cascade="all,delete-orphan")
    analyses: Mapped[list["Analysis"]] = relationship(back_populates="user", cascade="all,delete-orphan")
    roadmaps: Mapped[list["Roadmap"]] = relationship(back_populates="user", cascade="all,delete-orphan")
