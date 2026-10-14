"""Budget-aware grocery list generator.

Seed data of common Indian protein + vegetable sources with realistic INR prices.
Greedy knapsack-like selection to fit under `weekly_budget_inr`.
"""
from __future__ import annotations

import json
from pathlib import Path


_DATA_PATH = Path(__file__).parent.parent / "data" / "foods_inr.json"


def _load_db() -> dict:
    with open(_DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


def generate(weekly_budget_inr: float, vegetarian: bool, target_protein_g: float,
             weeks: int = 1) -> list[dict]:
    """Returns a list of grocery list dicts, one per week (defaults to 1)."""
    db = _load_db()
    pool = list(db["proteins_veg"] if vegetarian else db["proteins_veg"] + db["proteins_nonveg"])
    veg_pool = db["vegetables"]
    staple_pool = db["staples"]

    results = []
    per_week_budget = weekly_budget_inr / max(1, weeks)  # if user said ₹3000/month, ~₹750/week

    for _ in range(weeks):
        items, total = _select_items(pool, veg_pool, staple_pool, per_week_budget, target_protein_g)
        results.append({"total_inr": round(total, 2), "items": items})

    return results


def _select_items(proteins: list[dict], vegetables: list[dict], staples: list[dict],
                  budget: float, target_protein_g: float) -> tuple[list[dict], float]:
    items: list[dict] = []
    spent = 0.0
    protein_remaining = target_protein_g

    # Greedy: cheapest protein/INR first until protein target hit or budget exhausted
    proteins_sorted = sorted(proteins, key=lambda p: p["price_inr"] / max(1, p["protein_g"]))
    for p in proteins_sorted:
        if protein_remaining <= 0 or spent >= budget * 0.6:  # cap protein spend at 60% of budget
            break
        if spent + p["price_inr"] > budget * 0.6:
            continue
        items.append({
            "name": p["name"],
            "qty": p["qty"],
            "unit": p["unit"],
            "est_price": p["price_inr"],
            "category": "protein",
        })
        spent += p["price_inr"]
        protein_remaining -= p["protein_g"]

    # Fill vegetables
    veg_budget = min(budget * 0.3, budget - spent)
    veg_sorted = sorted(vegetables, key=lambda v: -v["nutrition_score"])
    veg_spend = 0.0
    for v in veg_sorted:
        if veg_spend + v["price_inr"] > veg_budget:
            continue
        items.append({
            "name": v["name"],
            "qty": v["qty"],
            "unit": v["unit"],
            "est_price": v["price_inr"],
            "category": "vegetable",
        })
        veg_spend += v["price_inr"]
    spent += veg_spend

    # Fill remaining with staples
    staple_spend = 0.0
    staple_budget = budget - spent
    for s in staples:
        if staple_spend + s["price_inr"] > staple_budget:
            continue
        items.append({
            "name": s["name"],
            "qty": s["qty"],
            "unit": s["unit"],
            "est_price": s["price_inr"],
            "category": "staple",
        })
        staple_spend += s["price_inr"]
    spent += staple_spend

    return items, spent
