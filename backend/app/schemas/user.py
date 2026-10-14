"""User schemas."""
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class UserCreate(BaseModel):
    height_cm: float = Field(..., gt=50, lt=260)
    weight_kg: float = Field(..., gt=20, lt=400)
    age: int = Field(..., ge=10, le=100)
    gender: str = Field(..., pattern="^(male|female|other)$")
    target_weight_kg: float = Field(..., gt=20, lt=400)
    budget_inr: float = Field(default=3000.0, ge=0)
    city: str = Field(..., min_length=1, max_length=64)
    vegetarian: bool = True
    gym_available: bool = True
    schedule: str = ""


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    height_cm: float
    weight_kg: float
    age: int
    gender: str
    target_weight_kg: float
    budget_inr: float
    city: str
    vegetarian: bool
    gym_available: bool
    schedule: str
    created_at: datetime
