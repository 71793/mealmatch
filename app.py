"""
MealMatch — Streamlit app entry point.

Run with:
    streamlit run app.py

Architecture:
    app.py           -> Streamlit UI, page routing, layout
    recipe_engine.py -> matching engine (ranks recipes vs. pantry)
    ingredients.py   -> ingredient normalization, synonym handling
    api_client.py    -> external API calls (Spoonacular, Unsplash)
    state.py         -> session state helpers (pantry, saved recipes, shopping list)
    meal_planner.py  -> weekly meal plan state & aggregations
    sample_data.py   -> offline recipe dataset used when no API key is set
"""

from __future__ import annotations

import streamlit as st

from ingredients import normalize_ingredient, suggest_ingredients
from recipe_engine import rank_recipes, build_shopping_list
from api_client import RecipeProvider
from state import init_session_state, get_pantry, add_to_pantry, remove_from_pantry
from state import get_saved_recipes, save_recipe, unsave_recipe
from state import get_shopping_list, add_to_shopping_list, clear_shopping_list
from state import get_dietary_filters, set_dietary_filters
import meal_planner as mp

# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="MealMatch — Cook with what you have",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_session_state()
mp.init_meal_plan()

# Cache the provider so we only build it once per session
@st.cache_resource
def get_provider() -> RecipeProvider:
    return RecipeProvider()

provider = get_provider()


# ---------------------------------------------------------------------------
# Sidebar — pantry management + dietary filters
# ---------------------------------------------------------------------------
def render_sidebar() -> None:
    st.sidebar.title("🥦 Your Pantry")
    st.sidebar.caption("Add what you have at home. We'll match recipes to it.")

    # --- Add ingredient ---
    with st.sidebar.form("add_ingredient_form", clear_on_submit=True):
        new_ing = st.text_input(
            "Add ingredient",
            placeholder="e.g. chicken, tomato, basil",
            key="new_ingredient_input",
        )
        submitted = st.form_submit_button("➕ Add", use_container_width=True)
        if submitted and new_ing.strip():
            normalized = normalize_ingredient(new_ing)
            add_to_pantry(normalized)
            st.toast(f"Added: {normalized}", icon="✅")

    # --- Quick suggestions for staples ---
    st.sidebar.markdown("**Quick add staples**")
    cols = st.sidebar.columns(2)
    for i, ing in enumerate(suggest_ingredients()):
        if cols[i % 2].button(ing, key=f"quick_{ing}", use_container_width=True):
            add_to_pantry(ing)
            st.rerun()

    st.sidebar.divider()

    # --- Current pantry ---
    pantry = get_pantry()
    st.sidebar.markdown(f"**In your pantry ({len(pantry)})**")
    if not pantry:
        st.sidebar.info("Your pantry is empty. Add some ingredients to get started.")
    else:
        for ing in sorted(pantry):
            c1, c2 = st.sidebar.columns([4, 1])
            c1.markdown(f"• {ing}")
            if c2.button("✕", key=f"rm_{ing}", help=f"Remove {ing}"):
                remove_from_pantry(ing)
                st.rerun()
        if st.sidebar.button("🗑️ Clear all", use_container_width=True):
            for ing in list(pantry):
                remove_from_pantry(ing)
            st.rerun()

    st.sidebar.divider()

    # --- Dietary filters ---
    st.sidebar.markdown("**Dietary preferences**")
    diets = ["vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb"]
    selected = st.sidebar.multiselect(
        "Restrictions",
        diets,
        default=get_dietary_filters(),
        label_visibility="collapsed",
    )
    set_dietary_filters(selected)


# ---------------------------------------------------------------------------
# Page: Discover recipes
# ---------------------------------------------------------------------------
def page_discover() -> None:
    st.title("🍳 Discover Recipes")
    st.caption(
        "Recipes ranked by how well they match what you already have. "
        "The fewer missing ingredients, the higher the rank."
    )

    pantry = get_pantry()
    diets = get_dietary_filters()

    if not pantry:
        st.warning("👈 Add some ingredients to your pantry first.")
        st.image(
            "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800",
            caption="Let's get cooking!",
            use_container_width=True,
        )
        return

    # Fetch recipes (uses API if key configured, else local sample data)
    with st.spinner("Finding recipes that match your pantry..."):
        recipes = provider.search_recipes(
            pantry=list(pantry), diets=diets, limit=30
        )

    if not recipes:
        st.error("No recipes found. Try adding more common ingredients.")
        return

    ranked = rank_recipes(recipes, pantry=pantry)

    st.success(f"Found **{len(ranked)}** matching recipes ✨")

    # --- Display recipes as cards ---
    cols_per_row = 3
    for row_start in range(0, len(ranked), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, recipe in enumerate(ranked[row_start : row_start + cols_per_row]):
            with cols[i]:
                _render_recipe_card(recipe)


def _render_recipe_card(recipe: dict) -> None:
    """Display a single recipe as a card."""
    with st.container(border=True):
        if recipe.get("image"):
            st.image(recipe["image"], use_container_width=True)

        st.markdown(f"### {recipe['title']}")

        # --- match metrics ---
        match_pct = int(recipe["match_score"] * 100)
        used = recipe["used_ingredients"]
        missing = recipe["missing_ingredients"]

        if match_pct >= 80:
            st.success(f"🎯 **{match_pct}% match** — you have almost everything!")
        elif match_pct >= 50:
            st.info(f"👍 **{match_pct}% match** — a few items missing")
        else:
            st.warning(f"📝 **{match_pct}% match** — bigger shopping list")

        c1, c2 = st.columns(2)
        c1.metric("You have", len(used))
        c2.metric("Missing", len(missing))

        if missing:
            with st.expander(f"🛒 Missing: {len(missing)} items"):
                for ing in missing:
                    st.markdown(f"• {ing}")

        # --- Action buttons ---
        b1, b2 = st.columns(2)
        if b1.button("💾 Save", key=f"save_{recipe['id']}", use_container_width=True):
            save_recipe(recipe)
            st.toast(f"Saved: {recipe['title']}", icon="💾")

        if b2.button(
            "🛒 Add missing",
            key=f"shop_{recipe['id']}",
            use_container_width=True,
            disabled=not missing,
        ):
            for ing in missing:
                add_to_shopping_list(ing)
            st.toast(f"Added {len(missing)} items to shopping list", icon="🛒")

        # --- Recipe details ---
        with st.expander("📖 View recipe"):
            st.markdown(f"**Ready in:** {recipe.get('ready_in_minutes', 'N/A')} min")
            st.markdown(f"**Servings:** {recipe.get('servings', 'N/A')}")

            if recipe.get("instructions"):
                st.markdown("**Instructions**")
                st.markdown(recipe["instructions"])
            else:
                st.caption("No detailed instructions available.")


# ---------------------------------------------------------------------------
# Page: Saved recipes
# ---------------------------------------------------------------------------
def page_saved() -> None:
    st.title("💾 Saved Recipes")
    saved = get_saved_recipes()

    if not saved:
        st.info("You haven't saved any recipes yet. Head to **Discover** to find some!")
        return

    st.caption(f"You have **{len(saved)}** saved recipes.")

    cols_per_row = 3
    for row_start in range(0, len(saved), cols_per_row):
        cols = st.columns(cols_per_row)
        for i, recipe in enumerate(saved[row_start : row_start + cols_per_row]):
            with cols[i]:
                with st.container(border=True):
                    if recipe.get("image"):
                        st.image(recipe["image"], use_container_width=True)
                    st.markdown(f"### {recipe['title']}")
                    st.caption(
                        f"⏱️ {recipe.get('ready_in_minutes', 'N/A')} min  •  "
                        f"🍽️ {recipe.get('servings', 'N/A')} servings"
                    )
                    if st.button(
                        "🗑️ Remove",
                        key=f"unsave_{recipe['id']}",
                        use_container_width=True,
                    ):
                        unsave_recipe(recipe["id"])
                        st.rerun()


# ---------------------------------------------------------------------------
# Page: Shopping list
# ---------------------------------------------------------------------------
def page_shopping() -> None:
    st.title("🛒 Shopping List")
    items = get_shopping_list()

    if not items:
        st.info(
            "Your shopping list is empty. Add missing ingredients from the "
            "**Discover** page."
        )
        return

    # Group by category if available, otherwise just list
    st.caption(f"**{len(items)}** items to buy")

    # --- Generate consolidated list ---
    consolidated = build_shopping_list(items)

    for category, ings in consolidated.items():
        st.markdown(f"### {category}")
        for ing in ings:
            checked = st.checkbox(ing, key=f"check_{ing}")
            # Note: in-session-only; persists until clear

    st.divider()
    c1, c2 = st.columns(2)

    if c1.button("📋 Copy as text", use_container_width=True):
        text = "\n".join(f"- {item}" for item in items)
        st.code(text, language="markdown")

    if c2.button("🗑️ Clear list", use_container_width=True, type="primary"):
        clear_shopping_list()
        st.rerun()


# ---------------------------------------------------------------------------
# Page: Meal Planner
# ---------------------------------------------------------------------------
def page_planner() -> None:
    st.title("📅 Weekly Meal Planner")
    st.caption(
        "Plan your week ahead. Pick from your saved recipes, see total "
        "nutrition, and auto-generate a shopping list for the whole week."
    )

    saved = get_saved_recipes()
    if not saved:
        st.warning(
            "📌 You haven't saved any recipes yet. Head to **Discover** to "
            "find recipes, then click **💾 Save** on the ones you like. "
            "They'll show up here as options to plan."
        )
        return

    plan = mp.get_plan()
    planned = mp.planned_count()

    # --- Top metrics row ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Meals planned", f"{planned} / 21")
    pantry_now = get_pantry()
    missing = mp.week_missing_ingredients(pantry_now)
    c2.metric("🛒 To buy this week", len(missing))
    nutr = mp.week_nutrition_summary()
    if nutr["calories"] is not None:
        c3.metric("🔥 Total kcal", f"{int(nutr['calories']):,}")
        c4.metric("🍗 Total protein", f"{int(nutr['protein'])} g")
    else:
        c3.metric("🔥 Total kcal", "—")
        c4.metric("🍗 Total protein", "—")

    st.divider()

    # --- Action buttons ---
    a1, a2, _ = st.columns([1, 1, 3])
    if a1.button(
        "🛒 Add week's missing items to shopping list",
        use_container_width=True,
        disabled=not missing,
    ):
        for ing in missing:
            add_to_shopping_list(ing)
        st.toast(
            f"Added {len(missing)} items to shopping list",
            icon="🛒",
        )

    if a2.button(
        "🗑️ Clear week",
        use_container_width=True,
        type="secondary",
        disabled=planned == 0,
    ):
        mp.clear_week()
        st.rerun()

    st.divider()

    # --- Build options for the dropdowns ---
    # We map a label like "Spaghetti Aglio e Olio" -> recipe dict.
    # The "(empty)" option lets users clear a slot.
    recipe_options = {"— (empty) —": None}
    for r in saved:
        # Use title as visible label; recipe id is implicit via the dict
        recipe_options[r["title"]] = r

    # --- The weekly grid ---
    # Each day is a row; each meal is a column inside that row.
    for day in mp.DAYS:
        st.markdown(f"### {day}")
        cols = st.columns(len(mp.MEALS))
        for col_idx, meal in enumerate(mp.MEALS):
            with cols[col_idx]:
                current = plan[day][meal]
                # Compute default index for the selectbox
                if current is None:
                    default_label = "— (empty) —"
                else:
                    default_label = current["title"]

                # Selectbox: pick a recipe (or empty)
                # We use a unique key per day+meal so Streamlit tracks state
                options_list = list(recipe_options.keys())
                # If a saved recipe was deleted while in the plan, fall back
                # gracefully to "(empty)" rather than crashing.
                if default_label not in options_list:
                    default_label = "— (empty) —"

                chosen_label = st.selectbox(
                    label=meal,
                    options=options_list,
                    index=options_list.index(default_label),
                    key=f"plan_{day}_{meal}",
                )
                chosen_recipe = recipe_options[chosen_label]

                # Sync back to plan if changed
                if chosen_recipe != current:
                    mp.set_slot(day, meal, chosen_recipe)

                # Show small recipe preview if a recipe is in the slot
                if chosen_recipe:
                    if chosen_recipe.get("image"):
                        st.image(
                            chosen_recipe["image"],
                            use_container_width=True,
                        )
                    st.caption(
                        f"⏱️ {chosen_recipe.get('ready_in_minutes', 'N/A')} min  "
                        f"• 🍽️ {chosen_recipe.get('servings', 'N/A')} servings"
                    )
        st.divider()

    # --- Missing ingredients summary ---
    if missing:
        with st.expander(f"🛒 Missing ingredients for the week ({len(missing)})"):
            # Group by category using the existing shopping-list logic
            grouped = build_shopping_list(missing)
            for category, ings in grouped.items():
                st.markdown(f"**{category}**")
                for ing in ings:
                    st.markdown(f"• {ing}")
    else:
        if planned > 0:
            st.success(
                "🎉 Your pantry covers everything you've planned! No shopping needed."
            )


# ---------------------------------------------------------------------------
# Main router
# ---------------------------------------------------------------------------
def main() -> None:
    render_sidebar()

    # Top-level navigation
    tab1, tab2, tab3, tab4 = st.tabs(
        ["🍳 Discover", "💾 Saved", "📅 Planner", "🛒 Shopping List"]
    )

    with tab1:
        page_discover()
    with tab2:
        page_saved()
    with tab3:
        page_planner()
    with tab4:
        page_shopping()

    # Footer
    st.markdown("---")
    st.caption(
        "**MealMatch** — Cook with what you have. Powered by Streamlit. "
        "Set `SPOONACULAR_API_KEY` in your environment to use live recipe data."
    )


if __name__ == "__main__":
    main()
