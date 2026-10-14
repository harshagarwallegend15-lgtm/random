"""GroceryList model — per roadmap week."""
from sqlalchemy import String, Integer, ForeignKey, Float
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB

from app.database import Base


class GroceryList(Base):
    __tablename__ = "grocery_lists"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    roadmap_id: Mapped[int] = mapped_column(ForeignKey("roadmaps.id", ondelete="CASCADE"), index=True)
    week: Mapped[int] = mapped_column(Integer, nullable=False)
    total_inr: Mapped[float] = mapped_column(Float, nullable=False)
    items: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)

    roadmap: Mapped["Roadmap"] = relationship(back_populates="grocery_lists")
