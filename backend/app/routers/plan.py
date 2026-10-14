"""Plan generation route: assembles roadmap + grocery + workout for a user."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.models import Analysis, GroceryList, Roadmap, User, WorkoutPlan
from app.schemas import PlanOut
from app.services import grocery, roadmap as roadmap_svc, workout

router = APIRouter(prefix="/plan", tags=["plan"])


@router.post("/{user_id}/generate", response_model=PlanOut, status_code=201)
def generate_plan(user_id: int, db: Session = Depends(get_db)):
    """Generate (or regenerate) the 12-week plan based on the latest analysis + profile."""
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    analysis = db.execute(
        select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.id.desc()).limit(1)
    ).scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=400, detail="Upload + analyse photos before generating plan")

    # Clear old plans
    for old in db.execute(select(Roadmap).where(Roadmap.user_id == user_id)).scalars().all():
        db.delete(old)
    db.flush()

    weeks_data = roadmap_svc.generate(
        weight_kg=user.weight_kg,
        height_cm=user.height_cm,
        age=user.age,
        gender=user.gender,
        target_weight_kg=user.target_weight_kg,
        schedule=user.schedule,
        weeks=12,
        vegetarian=user.vegetarian,
    )

    # Build roadmap rows + workouts + grocery
    roadmap_rows = []
    plan_payload_weeks = []
    weekly_budget_inr = user.budget_inr / 4  # monthly → weekly

    for week_data in weeks_data:
        week = week_data["week"]
        exercises_for_week = workout.generate(
            gym_available=user.gym_available,
            weak_muscles=analysis.weak_muscles or [],
            week=week,
            weeks_total=12,
        )

        # Grocery for the week (use protein target from this week's plan)
        grocery_lists = grocery.generate(
            weekly_budget_inr=weekly_budget_inr,
            vegetarian=user.vegetarian,
            target_protein_g=week_data["protein_g"] * 7,  # weekly protein target
            weeks=1,
        )
        grocery_data = grocery_lists[0]

        roadmap = Roadmap(
            user_id=user_id,
            week=week,
            calories=week_data["calories"],
            protein_g=week_data["protein_g"],
            carbs_g=week_data["carbs_g"],
            fats_g=week_data["fats_g"],
            workout_focus=week_data["workout_focus"],
            notes=week_data["notes"],
            workout_plans=[
                WorkoutPlan(day=d["day"], title=d["title"], exercises=d["exercises"])
                for d in exercises_for_week
            ],
            grocery_lists=[
                GroceryList(week=week, total_inr=grocery_data["total_inr"], items=grocery_data["items"])
            ],
        )
        db.add(roadmap)
        roadmap_rows.append(roadmap)
        plan_payload_weeks.append({
            "week": week,
            "calories": week_data["calories"],
            "protein_g": week_data["protein_g"],
            "carbs_g": week_data["carbs_g"],
            "fats_g": week_data["fats_g"],
            "workout_focus": week_data["workout_focus"],
            "notes": week_data["notes"],
            "workout_days": exercises_for_week,
        })

    db.commit()

    # Predict target date
    weekly_delta = 0.0
    history = db.execute(
        select(Analysis).where(Analysis.user_id == user_id).order_by(Analysis.id.asc())
    ).scalars().all()
    if len(history) >= 2:
        days = max(1, (history[-1].created_at - history[0].created_at).days or 7)
        weight_change = analysis.muscle_mass_kg - history[0].muscle_mass_kg
        weekly_delta = max(0.05, (abs(weight_change) / days) * 7)

    predicted_weeks, predicted_date = roadmap_svc.predict_target_date(
        weight_kg=user.weight_kg,
        target_weight_kg=user.target_weight_kg,
        weekly_delta_kg=weekly_delta or 0.3,
    )

    return PlanOut(
        user_id=user_id,
        weeks=12,
        roadmap=[{
            **w,
            "grocery": [{
                "week": w["week"],
                "total_inr": next(r for r in roadmap_rows if r.week == w["week"]).grocery_lists[0].total_inr,
                "items": next(r for r in roadmap_rows if r.week == w["week"]).grocery_lists[0].items,
            }],
        } for w in plan_payload_weeks],
        grocery=[{
            "week": r.week,
            "total_inr": r.grocery_lists[0].total_inr,
            "items": r.grocery_lists[0].items,
        } for r in roadmap_rows],
        predicted_target_weeks=predicted_weeks,
        predicted_target_date=predicted_date,
    )


@router.get("/{user_id}", response_model=PlanOut)
def get_plan(user_id: int, db: Session = Depends(get_db)):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    roadmaps = db.execute(
        select(Roadmap)
        .where(Roadmap.user_id == user_id)
        .order_by(Roadmap.week.asc())
        .options(selectinload(Roadmap.workout_plans), selectinload(Roadmap.grocery_lists))
    ).scalars().all()
    if not roadmaps:
        raise HTTPException(status_code=404, detail="No plan generated yet — call POST /plan/{user_id}/generate")

    return PlanOut(
        user_id=user_id,
        weeks=len(roadmaps),
        roadmap=[{
            "week": r.week,
            "calories": r.calories,
            "protein_g": r.protein_g,
            "carbs_g": r.carbs_g,
            "fats_g": r.fats_g,
            "workout_focus": r.workout_focus,
            "notes": r.notes,
            "workout_days": [
                {"day": wp.day, "title": wp.title, "exercises": wp.exercises}
                for wp in sorted(r.workout_plans, key=lambda x: x.day)
            ],
        } for r in roadmaps],
        grocery=[{
            "week": r.week,
            "total_inr": r.grocery_lists[0].total_inr if r.grocery_lists else 0,
            "items": r.grocery_lists[0].items if r.grocery_lists else [],
        } for r in roadmaps],
        predicted_target_weeks=0.0,
        predicted_target_date=None,
    )
