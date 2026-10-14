"""Plan-related schemas."""
from pydantic import BaseModel


class ExerciseOut(BaseModel):
    name: str
    sets: int
    reps: str
    video_url: str
    target_muscle: str


class WorkoutDayOut(BaseModel):
    day: int
    title: str
    exercises: list[ExerciseOut]


class RoadmapWeekOut(BaseModel):
    week: int
    calories: float
    protein_g: float
    carbs_g: float
    fats_g: float
    workout_focus: str
    notes: str | None = None
    workout_days: list[WorkoutDayOut]


class GroceryItemOut(BaseModel):
    name: str
    qty: float
    unit: str
    est_price: float
    category: str


class GroceryListOut(BaseModel):
    week: int
    total_inr: float
    items: list[GroceryItemOut]


class PlanOut(BaseModel):
    user_id: int
    weeks: int
    roadmap: list[RoadmapWeekOut]
    grocery: list[GroceryListOut]
    predicted_target_weeks: float
    predicted_target_date: str | None
