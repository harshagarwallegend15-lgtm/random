"""12-week calorie + macro roadmap generator.

Uses Mifflin-Storer for BMR, activity factor from schedule string, then builds
weekly deficits/surpluses toward the target weight over `weeks`.
"""
from __future__ import annotations

from typing import Literal

ActivityLevel = Literal["sedentary", "light", "moderate", "active", "very_active"]

# 0.45 kg/wk = 500 kcal/day deficit (mild) — minimum recommended for safe fat loss
SAFE_FAT_LOSS_KG_PER_WEEK = 0.45
SAFE_MUSCLE_GAIN_KG_PER_WEEK = 0.20


def infer_activity_level(schedule: str) -> ActivityLevel:
    s = (schedule or "").lower()
    # Most-active signal wins
    if any(k in s for k in ("intense", "athlete", "2x", "twice", "labour", "labor", "5x", "6x", "7x", "daily training")):
        return "very_active"
    if any(k in s for k in ("1 hour", "1h", "run", "gym daily", "4x", "5x", "6x")):
        return "active"
    if any(k in s for k in ("gym 3x", "gym 2x", "moderate", "30 min", "yoga", "active", "walk", "jog")):
        return "moderate"
    if any(k in s for k in ("desk", "office", "sedentary", "sitting", "study")):
        return "sedentary"
    return "light"


ACTIVITY_FACTORS = {
    "sedentary": 1.2,
    "light": 1.375,
    "moderate": 1.55,
    "active": 1.725,
    "very_active": 1.9,
}


def bmr_mifflin(weight_kg: float, height_cm: float, age: int, gender: str) -> float:
    base = 10 * weight_kg + 6.25 * height_cm - 5 * age
    return base + (5 if gender == "male" else -161)


def tdee(bmr: float, schedule: str) -> float:
    factor = ACTIVITY_FACTORS[infer_activity_level(schedule)]
    return bmr * factor


def _macro_split(calories: float, protein_g: float, fat_pct: float = 0.25) -> dict:
    protein_kcal = protein_g * 4
    fat_kcal = calories * fat_pct
    carbs_kcal = max(0, calories - protein_kcal - fat_kcal)
    return {
        "protein_g": round(protein_g, 1),
        "fats_g": round(fat_kcal / 9, 1),
        "carbs_g": round(carbs_kcal / 4, 1),
    }


def generate(weight_kg: float, height_cm: float, age: int, gender: str,
             target_weight_kg: float, schedule: str,
             weeks: int = 12, vegetarian: bool = True) -> list[dict]:
    """Returns a list of weekly roadmap dicts (one per week)."""
    delta = target_weight_kg - weight_kg  # negative = loss, positive = gain
    is_loss = delta < 0
    bmr = bmr_mifflin(weight_kg, height_cm, age, gender)
    maintenance = tdee(bmr, schedule)

    # Weekly kg change we aim for (capped at safe rates)
    if is_loss:
        weekly_kg = min(SAFE_FAT_LOSS_KG_PER_WEEK, abs(delta) / weeks)
    else:
        weekly_kg = min(SAFE_MUSCLE_GAIN_KG_PER_WEEK, abs(delta) / weeks)

    daily_delta_kcal = (weekly_kg * 7700) / 7  # 7700 kcal ≈ 1 kg fat
    if is_loss:
        daily_delta_kcal = -daily_delta_kcal  # negative for deficit
    # Floor for safety
    if is_loss:
        min_calories = 1400 if gender == "female" else 1600
    else:
        min_calories = maintenance + daily_delta_kcal

    # Protein floor: 1.6 g/kg (vegetarian slightly higher for plant protein digestibility)
    protein_per_kg = 1.8 if vegetarian else 1.6
    target_protein = protein_per_kg * weight_kg

    roadmap: list[dict] = []
    # Gentle step-down (or step-up) across weeks so the body adapts.
    # By week 1 we're at ~60% of the target delta, ramping to 100% in the final week.
    # This avoids a sudden aggressive cut and matches adaptation research.
    for week in range(1, weeks + 1):
        progress = (week - 1) / max(1, weeks - 1)  # 0.0 → 1.0 across the plan
        ramp = 0.6 + 0.4 * progress
        cal = maintenance + (daily_delta_kcal * ramp)
        if is_loss:
            cal = max(min_calories, cal)
        else:
            cal = max(min_calories, cal)
        macros = _macro_split(cal, target_protein)

        focus = _week_focus(week, is_loss)
        notes = _week_notes(week, is_loss, cal, maintenance)

        roadmap.append({
            "week": week,
            "calories": round(cal, 0),
            **macros,
            "workout_focus": focus,
            "notes": notes,
        })

    return roadmap


def _week_focus(week: int, is_loss: bool) -> str:
    if is_loss:
        if week <= 4:
            return "Foundation — full-body strength, habit building"
        if week <= 8:
            return "Progressive overload — push/pull/legs split"
        return "Intensification — supersets, HIIT finisher, refine weak points"
    else:
        if week <= 4:
            return "Hypertrophy base — higher volume, moderate load"
        if week <= 8:
            return "Strength-hypertrophy block — periodized loading"
        return "Peak strength — lower reps, heavier load, recovery focus"


def _week_notes(week: int, is_loss: bool, cal: float, maintenance: float) -> str:
    diff = cal - maintenance
    if is_loss:
        return f"Caloric deficit of {round(-diff)} kcal/day. Reassess at end of week {week}."
    if diff > 0:
        return f"Caloric surplus of {round(diff)} kcal/day for muscle gain."
    return "Maintenance calories — deload / skill week."


def predict_target_date(weight_kg: float, target_weight_kg: float, weekly_delta_kg: float,
                        current_week: int = 0) -> tuple[float, str | None]:
    """Extrapolate when the user will reach their target weight given observed weekly change.

    Returns (predicted_weeks_from_now, iso_date_or_None).
    """
    from datetime import date, timedelta

    remaining = abs(target_weight_kg - weight_kg)
    if remaining < 0.1 or weekly_delta_kg <= 0.01:
        return 0.0, date.today().isoformat()

    weeks_left = remaining / weekly_delta_kg
    target_date = date.today() + timedelta(weeks=round(weeks_left))
    return round(weeks_left, 1), target_date.isoformat()
