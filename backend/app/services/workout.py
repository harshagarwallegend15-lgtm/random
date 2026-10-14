"""Workout plan generator. Picks exercises by gym access, weak muscles, and intensity."""
from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import quote_plus


_DATA_PATH = Path(__file__).parent.parent / "data" / "exercises.json"


def _load_db() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def _yt(name: str) -> str:
    """Return a YouTube search URL (no API key needed)."""
    return f"https://www.youtube.com/results?search_query={quote_plus(name + ' exercise form')}"


def generate(gym_available: bool, weak_muscles: list[str], week: int, weeks_total: int = 12) -> list[dict]:
    """Returns a list of 4-6 workout day dicts for the given week."""
    db = _load_db()
    pool_key = "gym" if gym_available else "home"
    pool = db[pool_key]

    # Prioritize exercises that target weak muscles
    def score(ex: dict) -> float:
        s = 0.0
        for wm in weak_muscles:
            if wm in ex.get("targets", []):
                s += 2
        if week <= 4:
            s += ex.get("difficulty", 1) * -0.2  # prefer easy in foundation
        elif week >= 9:
            s += ex.get("difficulty", 1) * 0.2  # prefer hard in intensification
        return s

    pool_ranked = sorted(pool, key=score, reverse=True)

    # Day split
    if gym_available:
        days = _gym_split(pool_ranked, week)
    else:
        days = _home_split(pool_ranked, week)

    return days


def _gym_split(pool: list[dict], week: int) -> list[dict]:
    splits = [
        ("Push — Chest, Shoulders, Triceps", ["chest", "front_delts", "triceps"]),
        ("Pull — Back, Biceps, Rear Delts", ["lats", "biceps", "rear_delts", "rhomboids"]),
        ("Legs — Quads, Hamstrings, Glutes", ["quads", "hamstrings", "glutes"]),
        ("Upper + Core", ["chest", "back", "core"]),
    ]
    if week >= 9:
        splits.append(("HIIT + Weak-Point Finisher", []))

    out = []
    for i, (title, target_groups) in enumerate(splits, start=1):
        chosen = [e for e in pool if any(t in e.get("targets", []) for t in target_groups)][:5]
        if not chosen:
            chosen = pool[i * 3:(i + 1) * 3 + 2]
        out.append({
            "day": i,
            "title": title,
            "exercises": [
                {
                    "name": e["name"],
                    "sets": e["sets"].get(str(week), e["sets"]["default"]),
                    "reps": e["reps"],
                    "video_url": _yt(e["name"]),
                    "target_muscle": ", ".join(e.get("targets", [])),
                }
                for e in chosen
            ],
        })
    return out


def _home_split(pool: list[dict], week: int) -> list[dict]:
    days = [
        ("Full Body A", ["chest", "quads", "core"]),
        ("Full Body B", ["back", "glutes", "biceps"]),
        ("Mobility + Core", ["core", "hip_flexors"]),
    ]
    out = []
    for i, (title, target_groups) in enumerate(days, start=1):
        chosen = [e for e in pool if any(t in e.get("targets", []) for t in target_groups)][:5]
        if not chosen:
            chosen = pool[i:i + 4]
        out.append({
            "day": i,
            "title": title,
            "exercises": [
                {
                    "name": e["name"],
                    "sets": e["sets"].get(str(week), e["sets"]["default"]),
                    "reps": e["reps"],
                    "video_url": _yt(e["name"]),
                    "target_muscle": ", ".join(e.get("targets", [])),
                }
                for e in chosen
            ],
        })
    return out
