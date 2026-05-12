"""
External API client.

Wraps Spoonacular (recipe data) and Unsplash (food photography fallback).

Both keys are optional. If neither is set, the app falls back to a local
sample dataset so you can demo and develop without API quotas.

Set environment variables:
    SPOONACULAR_API_KEY=your_key_here
    UNSPLASH_ACCESS_KEY=your_key_here

Or create a .env file (and add `python-dotenv` to requirements).
"""

from __future__ import annotations

import os
from typing import Optional

import requests

from sample_data import SAMPLE_RECIPES


SPOONACULAR_BASE = "https://api.spoonacular.com"
UNSPLASH_BASE = "https://api.unsplash.com"

# Cache responses in-process to keep API calls down during development.
# Streamlit's @st.cache_data also works at the call site if preferred.
_recipe_cache: dict[str, list[dict]] = {}
_image_cache: dict[str, str] = {}


def _load_key(name: str) -> str:
    """
    Load an API key, checking both environment variables and Streamlit secrets.

    Streamlit Community Cloud injects secrets via ``st.secrets`` (TOML), while
    local development typically uses environment variables or a ``.env`` file.
    We support both so the same code runs in either environment.
    """
    # 1) Try environment variable (works locally and most cloud platforms)
    val = os.getenv(name, "").strip()
    if val:
        return val

    # 2) Fall back to st.secrets (Streamlit Cloud)
    try:
        import streamlit as st  # imported lazily so non-Streamlit users don't pay
        if name in st.secrets:
            return str(st.secrets[name]).strip()
    except Exception:
        # st.secrets raises if no secrets file is configured — that's fine.
        pass

    return ""


class RecipeProvider:
    """
    Single entry point for fetching recipe data.

    Falls back gracefully:
        Spoonacular -> SAMPLE_RECIPES (filtered locally)
    """

    def __init__(self) -> None:
        self.spoonacular_key = _load_key("SPOONACULAR_API_KEY")
        self.unsplash_key = _load_key("UNSPLASH_ACCESS_KEY")

    # ------------------------------------------------------------------
    # Recipe search
    # ------------------------------------------------------------------
    def search_recipes(
        self,
        pantry: list[str],
        diets: Optional[list[str]] = None,
        limit: int = 20,
    ) -> list[dict]:
        """
        Return a list of recipe dicts matching the given pantry & dietary filters.

        Each recipe dict has at minimum:
            id, title, image, ingredients (list[str]), ready_in_minutes,
            servings, instructions
        """
        diets = diets or []

        if self.spoonacular_key:
            try:
                return self._spoonacular_search(pantry, diets, limit)
            except Exception as e:
                # Don't crash the UI on API failures — fall back silently.
                print(f"[RecipeProvider] Spoonacular request failed: {e}")

        return self._local_search(pantry, diets, limit)

    # ------------------------------------------------------------------
    # Spoonacular implementation
    # ------------------------------------------------------------------
    def _spoonacular_search(
        self, pantry: list[str], diets: list[str], limit: int
    ) -> list[dict]:
        cache_key = f"{','.join(sorted(pantry))}|{','.join(sorted(diets))}|{limit}"
        if cache_key in _recipe_cache:
            return _recipe_cache[cache_key]

        # Step 1: Find recipes by ingredients
        params = {
            "apiKey": self.spoonacular_key,
            "ingredients": ",".join(pantry),
            "number": limit,
            "ranking": 1,  # 1 = maximize used ingredients
            "ignorePantry": True,
        }
        resp = requests.get(
            f"{SPOONACULAR_BASE}/recipes/findByIngredients", params=params, timeout=10
        )
        resp.raise_for_status()
        candidates = resp.json()

        # Step 2: For each candidate, get full info (ingredients, instructions)
        ids = ",".join(str(r["id"]) for r in candidates[:limit])
        if not ids:
            _recipe_cache[cache_key] = []
            return []

        info_resp = requests.get(
            f"{SPOONACULAR_BASE}/recipes/informationBulk",
            params={
                "apiKey": self.spoonacular_key,
                "ids": ids,
                "includeNutrition": "true",
            },
            timeout=10,
        )
        info_resp.raise_for_status()
        info_list = info_resp.json()

        # Step 3: Apply diet filters locally (Spoonacular has its own diet
        # endpoints but it's simpler to filter the results we have)
        results = []
        for info in info_list:
            if diets and not _matches_diets(info, diets):
                continue
            results.append(_normalize_spoonacular_recipe(info))

        _recipe_cache[cache_key] = results
        return results

    # ------------------------------------------------------------------
    # Local fallback
    # ------------------------------------------------------------------
    def _local_search(
        self, pantry: list[str], diets: list[str], limit: int
    ) -> list[dict]:
        """Filter the local sample dataset by dietary tags."""
        results = []
        for recipe in SAMPLE_RECIPES:
            tags = set(recipe.get("diets", []))
            if diets and not all(d in tags for d in diets):
                continue
            results.append(recipe)
        return results[:limit]

    # ------------------------------------------------------------------
    # Unsplash image fallback
    # ------------------------------------------------------------------
    def get_food_image(self, query: str) -> Optional[str]:
        """Fetch a food image from Unsplash. Returns URL or None."""
        if not self.unsplash_key:
            return None

        if query in _image_cache:
            return _image_cache[query]

        try:
            resp = requests.get(
                f"{UNSPLASH_BASE}/search/photos",
                params={"query": query + " food", "per_page": 1},
                headers={"Authorization": f"Client-ID {self.unsplash_key}"},
                timeout=5,
            )
            resp.raise_for_status()
            results = resp.json().get("results", [])
            if results:
                url = results[0]["urls"]["small"]
                _image_cache[query] = url
                return url
        except Exception as e:
            print(f"[RecipeProvider] Unsplash request failed: {e}")

        return None


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _matches_diets(recipe_info: dict, requested_diets: list[str]) -> bool:
    """Spoonacular returns boolean diet flags. Map them to our names."""
    diet_flags = {
        "vegetarian": recipe_info.get("vegetarian", False),
        "vegan": recipe_info.get("vegan", False),
        "gluten-free": recipe_info.get("glutenFree", False),
        "dairy-free": recipe_info.get("dairyFree", False),
        "low-carb": False,  # Not directly available; would need nutrition lookup
    }
    return all(diet_flags.get(d, False) for d in requested_diets)


def _extract_nutrition(info: dict) -> dict:
    """
    Pull calories/protein/carbs/fat per serving out of Spoonacular's nutrition
    structure. Returns an empty dict if the data isn't there so the planner
    knows to skip this recipe in totals.
    """
    nutrition = info.get("nutrition", {})
    nutrients = nutrition.get("nutrients", []) if nutrition else []
    if not nutrients:
        return {}

    # Build a quick lookup by nutrient name
    lookup = {n.get("name", "").lower(): n.get("amount", 0) for n in nutrients}

    return {
        "calories": lookup.get("calories", 0),
        "protein": lookup.get("protein", 0),
        "carbs": lookup.get("carbohydrates", 0),
        "fat": lookup.get("fat", 0),
    }


def _normalize_spoonacular_recipe(info: dict) -> dict:
    """Convert Spoonacular's response shape to our internal format."""
    # Simple list of normalized names — used by the matching engine.
    # We keep this exactly as before so nothing in the ranking logic breaks.
    ingredients: list[str] = []

    # Detailed view — amount, unit, full text — used by the UI for display.
    # We keep both in parallel; index N in one corresponds to index N in the other.
    ingredients_detailed: list[dict] = []

    for ing in info.get("extendedIngredients", []):
        name = ing.get("name") or ing.get("originalName") or ""
        if not name:
            continue

        ingredients.append(name)
        ingredients_detailed.append(
            {
                "name": name,
                "amount": ing.get("amount", 0),
                "unit": ing.get("unit", "") or "",
                # 'original' is the human-readable form: "2 large tomatoes, diced"
                "original": ing.get("original") or ing.get("originalString") or name,
            }
        )

    # Instructions: prefer the analyzedInstructions structure for clean steps
    instructions_text = ""
    analyzed = info.get("analyzedInstructions", [])
    if analyzed and analyzed[0].get("steps"):
        steps = analyzed[0]["steps"]
        instructions_text = "\n\n".join(
            f"{step['number']}. {step['step']}" for step in steps
        )
    else:
        instructions_text = info.get("instructions", "") or ""

    return {
        "id": info["id"],
        "title": info["title"],
        "image": info.get("image", ""),
        "ingredients": ingredients,
        "ingredients_detailed": ingredients_detailed,
        "ready_in_minutes": info.get("readyInMinutes", 0),
        "servings": info.get("servings", 0),
        "instructions": instructions_text,
        "diets": info.get("diets", []),
        "nutrition": _extract_nutrition(info),
    }
import os
import base64
import anthropic
def analyze_fridge_image(image_bytes: bytes) -> list:
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    image_data = base64.standard_b64encode(image_bytes).decode("utf-8")
    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": image_data,
                    },
                },
                {
                    "type": "text",
                    "text": "Analysiere dieses Kühlschrank-Foto. Liste alle sichtbaren Lebensmittel auf. Antworte NUR mit einer kommagetrennten Liste, z.B.: Milch, Eier, Käse, Tomaten"
                }
            ],
        }],
    )
    result = message.content[0].text
    return [item.strip() for item in result.split(",")]
