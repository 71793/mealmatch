"""
Meal Planner.

Adds a weekly meal-planning feature on top of the existing pantry/saved/shopping
structure. The plan is stored as a dict:

    {
        "Monday":    {"Breakfast": recipe_or_None, "Lunch": ..., "Dinner": ...},
        "Tuesday":   {...},
        ...
    }

Each slot holds a full recipe dict (same shape as saved recipes) or None.

Helpers here let the UI:
    * place / clear a recipe in a slot
    * pull the whole plan's missing ingredients into the shopping list
    * compute aggregate nutrition for the week (best-effort: many recipes
      won't have nutrition data, in which case the field is None)
"""

from __future__ import annotations

import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DAYS: list[str] = [
    "Monday", "Tuesday", "Wednesday", "Thursday",
    "Friday", "Saturday", "Sunday",
]
MEALS: list[str] = ["Breakfast", "Lunch", "Dinner"]

_K_PLAN = "meal_plan"


def init_meal_plan() -> None:
    """Initialize an empty plan if not already set. Called from app startup."""
    if _K_PLAN not in st.session_state:
        st.session_state[_K_PLAN] = {
            day: {meal: None for meal in MEALS} for day in DAYS
        }


# ---------------------------------------------------------------------------
# Plan accessors
# ---------------------------------------------------------------------------
def get_plan() -> dict[str, dict[str, dict | None]]:
    init_meal_plan()
    return st.session_state[_K_PLAN]


def set_slot(day: str, meal: str, recipe: dict | None) -> None:
    """Place a recipe (or clear with None) into a specific slot."""
    init_meal_plan()
    if day in DAYS and meal in MEALS:
        st.session_state[_K_PLAN][day][meal] = recipe


def clear_slot(day: str, meal: str) -> None:
    set_slot(day, meal, None)


def clear_week() -> None:
    """Empty the entire plan."""
    st.session_state[_K_PLAN] = {
        day: {meal: None for meal in MEALS} for day in DAYS
    }


# ---------------------------------------------------------------------------
# Aggregations
# ---------------------------------------------------------------------------
def planned_recipes() -> list[dict]:
    """Flat list of every recipe currently in the plan (with duplicates)."""
    plan = get_plan()
    out = []
    for day in DAYS:
        for meal in MEALS:
            r = plan[day][meal]
            if r is not None:
                out.append(r)
    return out


def planned_count() -> int:
    return len(planned_recipes())


def week_missing_ingredients(pantry: set[str]) -> list[str]:
    """
    Aggregate the missing ingredients across the whole week, deduplicated.

    Uses the same matching logic the rest of the app uses, so "tomato" in
    pantry covers "cherry tomato" in a recipe (and vice versa).
    """
    # Imported here to avoid a circular import at module load
    from ingredients import ingredients_match, normalize_ingredient

    pantry_set = {normalize_ingredient(p) for p in pantry if p}
    missing: set[str] = set()

    for recipe in planned_recipes():
        for r_ing in recipe.get("ingredients", []):
            normalized = normalize_ingredient(r_ing)
            if not normalized:
                continue
            # Skip if pantry already covers it
            if any(ingredients_match(p, r_ing) for p in pantry_set):
                continue
            missing.add(normalized)

    return sorted(missing)


def week_nutrition_summary() -> dict[str, float | None]:
    """
    Sum up calories / protein / carbs / fat across the planned recipes.

    Recipes may not have nutrition data (e.g. when fetched without the
    `includeNutrition` flag). We only sum what's present; if nothing in
    the plan has nutrition data, the values are returned as None so the
    UI can show a friendly placeholder.
    """
    totals = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
    found_any = False

    for recipe in planned_recipes():
        nut = recipe.get("nutrition", {}) or {}
        if not nut:
            continue
        found_any = True
        totals["calories"] += float(nut.get("calories", 0) or 0)
        totals["protein"] += float(nut.get("protein", 0) or 0)
        totals["carbs"] += float(nut.get("carbs", 0) or 0)
        totals["fat"] += float(nut.get("fat", 0) or 0)

    if not found_any:
        return {k: None for k in totals}
    return totals
