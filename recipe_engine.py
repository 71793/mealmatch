"""
Recipe matching & ranking engine.

This is the heart of MealMatch. We score each recipe against the user's pantry
and rank by:

    1. Match coverage  -> what fraction of the recipe's ingredients you have?
    2. Pantry usage    -> how many of your pantry items does this recipe use?
                          (rewards recipes that "use what's about to expire")
    3. Total complexity -> light penalty for very long ingredient lists.

The result is a single 0-1 score we use to sort. Tweak weights as you like.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Iterable

from ingredients import normalize_ingredient, ingredients_match


# -----------------------------------------------------------------------------
# Ranking weights (tweak these to change behavior)
# -----------------------------------------------------------------------------
W_COVERAGE = 0.70   # most important: how complete the recipe is from your pantry
W_USAGE = 0.20      # rewards recipes that use a lot of what you have
W_SIMPLICITY = 0.10 # mild bonus for shorter recipes


def _score_recipe(recipe: dict, pantry: set[str]) -> tuple[float, list[str], list[str]]:
    """
    Compute a 0-1 match score for a single recipe.

    Returns
    -------
    score : float
    used : list of pantry items the recipe matched
    missing : list of recipe ingredients the user doesn't have
    """
    recipe_ings = recipe.get("ingredients", [])
    if not recipe_ings:
        return 0.0, [], []

    used: list[str] = []
    missing: list[str] = []

    for r_ing in recipe_ings:
        matched_pantry_item = None
        for p_ing in pantry:
            if ingredients_match(p_ing, r_ing):
                matched_pantry_item = p_ing
                break
        if matched_pantry_item:
            used.append(matched_pantry_item)
        else:
            missing.append(r_ing)

    n_total = len(recipe_ings)
    n_used = len(used)

    coverage = n_used / n_total if n_total else 0.0
    usage = n_used / len(pantry) if pantry else 0.0
    # short recipes get a small bonus, capped
    simplicity = max(0.0, 1.0 - (n_total / 20.0))

    score = (
        W_COVERAGE * coverage
        + W_USAGE * usage
        + W_SIMPLICITY * simplicity
    )

    return score, used, missing


def rank_recipes(recipes: list[dict], pantry: Iterable[str]) -> list[dict]:
    """
    Rank a list of recipes against the user's pantry.

    Each recipe in the output gets these new keys:
        match_score        : float (0-1)
        used_ingredients   : list[str]
        missing_ingredients: list[str]

    Recipes are returned sorted by descending match_score.
    """
    pantry_set = {normalize_ingredient(p) for p in pantry if p}

    enriched = []
    for r in recipes:
        score, used, missing = _score_recipe(r, pantry_set)
        enriched.append(
            {
                **r,
                "match_score": round(score, 3),
                "used_ingredients": used,
                "missing_ingredients": missing,
            }
        )

    enriched.sort(key=lambda x: x["match_score"], reverse=True)
    return enriched


# -----------------------------------------------------------------------------
# Shopping list helpers
# -----------------------------------------------------------------------------
# Very rough category mapping. In production you'd pull this from the API
# or build a proper ingredient ontology.
CATEGORIES: dict[str, str] = {
    "🥬 Produce": [
        "tomato", "onion", "garlic", "lettuce", "spinach", "kale",
        "carrot", "celery", "potato", "bell pepper", "scallion",
        "cilantro", "basil", "parsley", "lemon", "lime", "avocado",
        "cucumber", "zucchini", "eggplant", "mushroom", "broccoli",
        "cherry tomato", "arugula", "ginger", "chili pepper",
    ],
    "🥩 Meat & Seafood": [
        "chicken", "beef", "pork", "ground beef", "shrimp", "salmon",
        "tuna", "bacon", "sausage", "turkey", "lamb", "fish",
    ],
    "🥛 Dairy & Eggs": [
        "milk", "butter", "cheese", "egg", "yogurt", "cream",
        "parmesan", "mozzarella", "feta", "sour cream",
    ],
    "🌾 Pantry & Grains": [
        "rice", "pasta", "flour", "bread", "oats", "quinoa",
        "noodle", "lentil", "chickpeas", "black beans",
    ],
    "🧂 Spices & Condiments": [
        "salt", "black pepper", "olive oil", "vinegar", "soy sauce",
        "sugar", "honey", "mustard", "ketchup", "mayonnaise",
        "paprika", "cumin", "oregano", "thyme", "rosemary",
    ],
}


def _categorize(ingredient: str) -> str:
    """Return the best-fit category for an ingredient."""
    norm = normalize_ingredient(ingredient)
    for category, items in CATEGORIES.items():
        for item in items:
            if item in norm or norm in item:
                return category
    return "🛒 Other"


def build_shopping_list(items: list[str]) -> dict[str, list[str]]:
    """
    Group shopping list items by category and de-duplicate.

    Returns an ordered dict where keys are category labels and values are
    sorted, deduplicated ingredient lists.
    """
    grouped: dict[str, set[str]] = defaultdict(set)
    for item in items:
        category = _categorize(item)
        grouped[category].add(normalize_ingredient(item))

    # Return sorted lists in a stable category order
    ordered: dict[str, list[str]] = {}
    for category in list(CATEGORIES.keys()) + ["🛒 Other"]:
        if category in grouped:
            ordered[category] = sorted(grouped[category])
    return ordered
