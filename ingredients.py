"""
Ingredient normalization & synonym handling.

Handles the "scallion vs green onion" problem your team flagged as one
of the core technical challenges. The approach:

1. Lowercase + strip + singularize.
2. Map known synonyms to a canonical form (e.g. "green onion" -> "scallion").
3. Strip common modifiers ("fresh", "chopped", "diced", etc.).

For more advanced matching you could plug in a fuzzy-match library like
`rapidfuzz` or even an embedding-based matcher (sentence-transformers).
"""

from __future__ import annotations

import re

# -----------------------------------------------------------------------------
# Synonym dictionary — extend as needed
# -----------------------------------------------------------------------------
# Maps {alias: canonical_name}. Keep keys lowercase singular.
SYNONYMS: dict[str, str] = {
    # alliums
    "green onion": "scallion",
    "spring onion": "scallion",
    "shallot": "shallot",
    # peppers
    "bell pepper": "bell pepper",
    "capsicum": "bell pepper",
    "sweet pepper": "bell pepper",
    "chili": "chili pepper",
    "chilli": "chili pepper",
    # herbs
    "coriander": "cilantro",
    "coriander leaves": "cilantro",
    # tomato
    "tomatoe": "tomato",
    "cherry tomatoes": "cherry tomato",
    # cheese
    "parmesan cheese": "parmesan",
    "parmiggiano": "parmesan",
    "parmigiano": "parmesan",
    # other staples
    "aubergine": "eggplant",
    "courgette": "zucchini",
    "rocket": "arugula",
    "prawn": "shrimp",
    "minced beef": "ground beef",
    "minced meat": "ground beef",
    "chickpea": "chickpeas",
    "garbanzo": "chickpeas",
    "garbanzo beans": "chickpeas",
    # spices
    "black peppercorn": "black pepper",
    "peppercorn": "black pepper",
}

# Common modifiers we strip out before matching.
# Note: "ground" is intentionally NOT here because "ground beef" is a distinct
# product from "beef". Same logic for other compound-noun modifiers.
MODIFIERS: set[str] = {
    "fresh",
    "frozen",
    "dried",
    "chopped",
    "diced",
    "sliced",
    "minced",
    "grated",
    "shredded",
    "crushed",
    "raw",
    "cooked",
    "organic",
    "large",
    "small",
    "medium",
    "whole",
    "half",
    "ripe",
    "unsalted",
    "salted",
    "extra",
    "virgin",
    "cold",
    "hot",
}

# A small library of common staples for the "Quick Add" UI
COMMON_STAPLES: list[str] = [
    "olive oil",
    "salt",
    "black pepper",
    "garlic",
    "onion",
    "tomato",
    "egg",
    "butter",
    "flour",
    "rice",
    "pasta",
    "milk",
]


def _singularize(word: str) -> str:
    """Very simple singularization. Good enough for our use case."""
    if word.endswith("ies") and len(word) > 3:
        return word[:-3] + "y"
    if word.endswith("ses") or word.endswith("xes") or word.endswith("zes"):
        return word[:-2]
    if word.endswith("s") and not word.endswith("ss") and len(word) > 3:
        return word[:-1]
    return word


def normalize_ingredient(raw: str) -> str:
    """
    Convert a free-text ingredient string to its canonical form.

    Examples
    --------
    >>> normalize_ingredient("Fresh Green Onions")
    'scallion'
    >>> normalize_ingredient("2 large eggs")
    'egg'
    >>> normalize_ingredient("Chopped Tomatoes")
    'tomato'
    """
    if not raw:
        return ""

    # Lowercase + strip
    text = raw.lower().strip()

    # Remove numbers and units (e.g. "2 cups", "500g")
    text = re.sub(r"\b\d+(\.\d+)?\s*(g|kg|ml|l|oz|lb|cup|cups|tsp|tbsp|tablespoon|teaspoon)?\b", "", text)
    text = re.sub(r"[^a-z\s-]", "", text)  # keep letters, spaces, hyphens
    text = re.sub(r"\s+", " ", text).strip()

    # Try synonym lookup before stripping modifiers
    if text in SYNONYMS:
        return SYNONYMS[text]

    # Strip modifiers
    tokens = [t for t in text.split() if t not in MODIFIERS]
    text = " ".join(tokens).strip()

    # Try synonym lookup after stripping
    if text in SYNONYMS:
        return SYNONYMS[text]

    # Singularize last word (e.g. "tomatoes" -> "tomato")
    if tokens:
        tokens[-1] = _singularize(tokens[-1])
        text = " ".join(tokens)

    if text in SYNONYMS:
        return SYNONYMS[text]

    return text


def ingredients_match(pantry_item: str, recipe_item: str) -> bool:
    """
    Check whether a pantry item satisfies a recipe ingredient.

    A recipe asks for "tomato"; a pantry has "cherry tomato". We say yes —
    because the recipe one is more general. We use substring matching as a
    cheap heuristic on the normalized forms.
    """
    p = normalize_ingredient(pantry_item)
    r = normalize_ingredient(recipe_item)

    if not p or not r:
        return False
    if p == r:
        return True
    # If recipe asks for the more general form, pantry's specific form counts
    if r in p or p in r:
        return True
    return False


def suggest_ingredients() -> list[str]:
    """Return the staples list for the sidebar quick-add."""
    return COMMON_STAPLES
