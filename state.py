"""
Session state management.

Wraps Streamlit's `st.session_state` so the rest of the app doesn't have to
sprinkle string keys everywhere. This is the "clean state management system"
your team flagged as a key challenge.

Note on persistence:
    By default, session_state lives only as long as the user's browser tab.
    To persist across sessions, you'd swap these functions for SQLite, a
    JSON file, or a backend like Firebase. The interface stays the same.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

# Keys we manage. Centralized so nothing hardcodes raw strings.
_K_PANTRY = "pantry"
_K_SAVED = "saved_recipes"
_K_SHOPPING = "shopping_list"
_K_DIETS = "dietary_filters"


def init_session_state() -> None:
    """Initialize all keys with sensible defaults if they don't exist."""
    if _K_PANTRY not in st.session_state:
        st.session_state[_K_PANTRY] = set()
    if _K_SAVED not in st.session_state:
        st.session_state[_K_SAVED] = []
    if _K_SHOPPING not in st.session_state:
        st.session_state[_K_SHOPPING] = []
    if _K_DIETS not in st.session_state:
        st.session_state[_K_DIETS] = []


# ---------------------------------------------------------------------------
# Pantry
# ---------------------------------------------------------------------------
def get_pantry() -> set[str]:
    return st.session_state[_K_PANTRY]


def add_to_pantry(ingredient: str) -> None:
    if ingredient.strip():
        st.session_state[_K_PANTRY].add(ingredient.strip())


def remove_from_pantry(ingredient: str) -> None:
    st.session_state[_K_PANTRY].discard(ingredient)


# ---------------------------------------------------------------------------
# Saved recipes
# ---------------------------------------------------------------------------
def get_saved_recipes() -> list[dict]:
    return st.session_state[_K_SAVED]


def save_recipe(recipe: dict) -> None:
    saved = st.session_state[_K_SAVED]
    if not any(r["id"] == recipe["id"] for r in saved):
        saved.append(recipe)


def unsave_recipe(recipe_id: int | str) -> None:
    st.session_state[_K_SAVED] = [
        r for r in st.session_state[_K_SAVED] if r["id"] != recipe_id
    ]


def is_saved(recipe_id: int | str) -> bool:
    return any(r["id"] == recipe_id for r in st.session_state[_K_SAVED])


# ---------------------------------------------------------------------------
# Shopping list
# ---------------------------------------------------------------------------
def get_shopping_list() -> list[str]:
    return st.session_state[_K_SHOPPING]


def add_to_shopping_list(item: str) -> None:
    item = item.strip()
    if item and item not in st.session_state[_K_SHOPPING]:
        st.session_state[_K_SHOPPING].append(item)


def clear_shopping_list() -> None:
    st.session_state[_K_SHOPPING] = []


# ---------------------------------------------------------------------------
# Dietary filters
# ---------------------------------------------------------------------------
def get_dietary_filters() -> list[str]:
    return st.session_state[_K_DIETS]


def set_dietary_filters(filters: list[str]) -> None:
    st.session_state[_K_DIETS] = list(filters)
