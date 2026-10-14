"""Photo model — one row per uploaded image (3 per set)."""
from datetime import datetime
from sqlalchemy import String, Integer, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    angle: Mapped[str] = mapped_column(String(16), nullable=False)  # front|side|back
    cloudinary_url: Mapped[str] = mapped_column(String(512), nullable=False)
    cloudinary_public_id: Mapped[str] = mapped_column(String(256), nullable=False)
    set_id: Mapped[int] = mapped_column(Integer, index=True)  # groups 3 photos from one upload
    landmarks: Mapped[dict] = mapped_column(JSONB, nullable=True)  # cached MediaPipe landmarks
    taken_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="photos")
