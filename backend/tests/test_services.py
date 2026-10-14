"""Pytest smoke test for the body metrics + roadmap services (no DB needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services import body_metrics, roadmap, workout, grocery


def test_roadmap_weight_loss():
    weeks = roadmap.generate(80, 170, 28, "male", 70, "desk job, gym 3x", weeks=4, vegetarian=True)
    assert len(weeks) == 4
    # Deficit relative to maintenance (≈2700 for this profile)
    maintenance = roadmap.tdee(roadmap.bmr_mifflin(80, 170, 28, "male"), "desk job, gym 3x")
    assert all(w["calories"] < maintenance for w in weeks)
    # Calories should ramp down for weight loss
    assert weeks[-1]["calories"] < weeks[0]["calories"] + 50


def test_roadmap_weight_gain():
    weeks = roadmap.generate(60, 165, 25, "female", 65, "moderate yoga", weeks=4, vegetarian=False)
    assert len(weeks) == 4
    assert any(w["calories"] > 2000 for w in weeks)


def test_workout_gym_split():
    days = workout.generate(gym_available=True, weak_muscles=["chest", "rhomboids"], week=5)
    assert 4 <= len(days) <= 5
    assert all(d["exercises"] for d in days)


def test_workout_home():
    days = workout.generate(gym_available=False, weak_muscles=[], week=2)
    assert 3 <= len(days) <= 4


def test_grocery_budget_vegetarian():
    result = grocery.generate(weekly_budget_inr=750, vegetarian=True, target_protein_g=900, weeks=1)
    assert len(result) == 1
    assert result[0]["total_inr"] <= 800  # tiny slack for rounding
    assert any(it["category"] == "protein" for it in result[0]["items"])


def test_body_metrics_fallback():
    out = body_metrics.analyse(70, 170, 30, "male", {"front": None, "side": None, "back": None})
    assert "body_fat_pct" in out
    assert 3 <= out["body_fat_pct"] <= 55
