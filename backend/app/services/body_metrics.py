"""Body composition heuristics built on top of MediaPipe landmarks.

All estimates are *heuristic*. Documented as estimates, not medical-grade.
"""
from __future__ import annotations

import math
from typing import Any


def _euclid(a: dict, b: dict) -> float:
    return math.hypot(a["x"] - b["x"], a["y"] - b["y"])


def _mid(p1: dict, p2: dict) -> dict:
    return {"x": (p1["x"] + p2["x"]) / 2, "y": (p1["y"] + p2["y"]) / 2}


def estimate_body_fat_pct(weight_kg: float, height_cm: float, age: int, gender: str,
                          landmarks: dict[str, dict]) -> float:
    """Bland-Altman-style heuristic using BMI + waist/height ratio (proxy for US Navy)."""
    bmi = weight_kg / ((height_cm / 100) ** 2)

    waist_proxy = 0.0
    waist_proxy_source = 0
    for angle_data in (landmarks or {}).values():
        if not angle_data:
            continue
        pts = angle_data["points"]
        if "left_hip" in pts and "right_hip" in pts and "left_shoulder" in pts and "right_shoulder" in pts:
            shoulder = _mid(pts["left_shoulder"], pts["right_shoulder"])
            hip = _mid(pts["left_hip"], pts["right_hip"])
            waist_proxy += _euclid(shoulder, hip)
            waist_proxy_source += 1
    waist_proxy = (waist_proxy / waist_proxy_source) if waist_proxy_source else None

    # Base BF% from BMI (Deurenberg formula approximation)
    base = 1.20 * bmi + 0.23 * age - (10.8 if gender == "male" else 0) - 5.4

    # If waist/height ratio deviates from BMI expectation, nudge ±5%
    if waist_proxy is not None and height_cm > 0:
        whtr = waist_proxy / 1.0  # landmark units, treat as relative
        # Heuristic: wider torso relative to height → higher BF%
        bmi_implied = bmi
        if whtr > 0.6 and bmi_implied < 28:
            base += 3
        elif whtr < 0.4 and bmi_implied > 22:
            base -= 3

    return max(3.0, min(55.0, round(base, 1)))


def estimate_lean_mass(weight_kg: float, body_fat_pct: float) -> tuple[float, float]:
    """Returns (lean_mass_kg, muscle_mass_kg)."""
    lean = weight_kg * (1 - body_fat_pct / 100)
    # Skeletal muscle is ~40-50% of lean mass for average adults
    muscle = lean * 0.45
    return round(lean, 1), round(muscle, 1)


def assess_posture(landmarks: dict[str, dict]) -> tuple[float, list[str], dict]:
    """Score posture 0-100, list weak-muscle hints, and detail dict per angle."""
    score = 100.0
    weak: list[str] = []
    details: dict[str, Any] = {}

    front = (landmarks or {}).get("front")
    side = (landmarks or {}).get("side")
    back = (landmarks or {}).get("back")

    # Front: shoulder level + hip level
    if front:
        pts = front["points"]
        sh_diff = abs(pts["left_shoulder"]["y"] - pts["right_shoulder"]["y"])
        hip_diff = abs(pts["left_hip"]["y"] - pts["right_hip"]["y"])
        # 0.05 in normalized coords ≈ 5% head height tilt
        score -= min(20, sh_diff * 200)
        score -= min(15, hip_diff * 200)
        details["front"] = {"shoulder_tilt": round(sh_diff, 4), "hip_tilt": round(hip_diff, 4)}
        if sh_diff > 0.04:
            weak.append("lower_trapezius")
        if hip_diff > 0.04:
            weak.append("glutes" if pts["left_hip"]["y"] > pts["right_hip"]["y"] else "hip_abductors")

    # Side: forward head + rounded shoulders
    if side:
        pts = side["points"]
        shoulder = _mid(pts["left_shoulder"], pts["right_shoulder"])
        ear_proxy = pts["nose"]  # nose as ear proxy
        forward_head = ear_proxy["x"] - shoulder["x"]
        # If nose is in front of shoulders by > 0.05 in x
        score -= min(25, abs(forward_head) * 250)
        details["side"] = {"forward_head_offset": round(forward_head, 4)}
        if forward_head > 0.05:
            weak.extend(["upper_trapezius", "levator_scapulae"])
            weak.append("deep_neck_flexors")
        if forward_head < -0.02:
            weak.append("pectoralis_major")

    # Back: scapular symmetry (shoulder tilt is the main signal)
    if back:
        pts = back["points"]
        scap_diff = abs(pts["left_shoulder"]["y"] - pts["right_shoulder"]["y"])
        score -= min(20, scap_diff * 200)
        details["back"] = {"scapular_tilt": round(scap_diff, 4)}
        if scap_diff > 0.04:
            weak.append("rhomboids")
            weak.append("middle_trapezius")

    # De-duplicate while preserving order
    seen = set()
    weak_dedup = [m for m in weak if not (m in seen or seen.add(m))]

    score = max(0.0, min(100.0, round(score, 1)))
    return score, weak_dedup, details


def fat_distribution(landmarks: dict[str, dict]) -> dict[str, str]:
    """Map fat distribution into apple/pear/balanced buckets using landmark ratios."""
    front = (landmarks or {}).get("front")
    if not front:
        return {"pattern": "balanced", "primary_region": "torso", "notes": "insufficient_data"}

    pts = front["points"]
    shoulder_w = _euclid(pts["left_shoulder"], pts["right_shoulder"])
    hip_w = _euclid(pts["left_hip"], pts["right_hip"])
    torso_h = _euclid(_mid(pts["left_shoulder"], pts["right_shoulder"]),
                      _mid(pts["left_hip"], pts["right_hip"]))

    if hip_w <= 0 or torso_h <= 0:
        return {"pattern": "balanced", "primary_region": "torso", "notes": "degenerate_ratio"}

    whr = hip_w / shoulder_w if shoulder_w else 1.0
    if whr > 1.05:
        return {"pattern": "pear", "primary_region": "hips_glutes", "notes": f"whr={whr:.2f}"}
    if whr < 0.95:
        return {"pattern": "apple", "primary_region": "abdomen", "notes": f"whr={whr:.2f}"}
    return {"pattern": "balanced", "primary_region": "torso", "notes": f"whr={whr:.2f}"}


def analyse(weight_kg: float, height_cm: float, age: int, gender: str,
            landmarks: dict[str, dict]) -> dict:
    """Top-level: returns body_fat, lean, muscle, posture, weak_muscles, fat_distribution, notes."""
    bf = estimate_body_fat_pct(weight_kg, height_cm, age, gender, landmarks)
    lean, muscle = estimate_lean_mass(weight_kg, bf)
    posture, weak, details = assess_posture(landmarks)
    fat = fat_distribution(landmarks)

    notes_bits = []
    if bf > 25:
        notes_bits.append("Higher estimated body fat — focus on caloric deficit + resistance training.")
    if bf < 12:
        notes_bits.append("Lean composition — prioritise protein and progressive overload.")
    if posture < 70:
        notes_bits.append("Posture imbalances detected — corrective exercises added to plan.")
    if not any(landmarks.values()):
        notes_bits.append("Could not detect a person in some photos — estimates may be approximate.")

    return {
        "body_fat_pct": bf,
        "lean_mass_kg": lean,
        "muscle_mass_kg": muscle,
        "posture_score": posture,
        "weak_muscles": weak,
        "fat_distribution": fat,
        "posture_details": details,
        "notes": " ".join(notes_bits) or "Looks good — keep consistent.",
    }


def delta_vs_previous(current: dict, previous: dict | None) -> dict:
    """Compare current analysis to previous for the weekly re-analyze flow."""
    if not previous:
        return {"first_analysis": True, "muscle_change_kg": 0.0, "fat_change_pct": 0.0, "posture_change": 0.0}
    return {
        "first_analysis": False,
        "muscle_change_kg": round(current["muscle_mass_kg"] - previous["muscle_mass_kg"], 2),
        "fat_change_pct": round(current["body_fat_pct"] - previous["body_fat_pct"], 2),
        "posture_change": round(current["posture_score"] - previous["posture_score"], 1),
    }
