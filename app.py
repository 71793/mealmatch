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

# ---------------------------------------------------------------------------
# Airbnb-inspired theme
# ---------------------------------------------------------------------------
# Custom CSS to give the app a polished, modern look:
#   - Rounded image corners, subtle card shadows
#   - Coral/pink accent color (#FF385C, Airbnb's signature)
#   - Generous spacing and clean typography
#   - Hover effects on interactive elements
st.markdown(
    """
    <style>
    /* --- Typography --- */
    html, body, [class*="css"] {
        font-family: 'Circular', -apple-system, BlinkMacSystemFont,
                     'Segoe UI', Roboto, 'Helvetica Neue', sans-serif;
    }
    h1 {
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }
    h2, h3 {
        font-weight: 600 !important;
        letter-spacing: -0.01em;
    }

    /* --- Rounded images (Airbnb's hallmark) --- */
    .stImage > img {
        border-radius: 16px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    .stImage > img:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    }

    /* --- Cards: lift bordered containers with shadow and rounding --- */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 16px !important;
        border: 1px solid rgba(0, 0, 0, 0.06) !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        padding: 16px !important;
        transition: transform 0.25s ease, box-shadow 0.25s ease;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 12px 28px rgba(0, 0, 0, 0.10);
        transform: translateY(-4px);
    }

    /* --- Buttons: Airbnb-style coral with rounded corners --- */
    .stButton > button {
        border-radius: 8px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.2rem !important;
        transition: all 0.2s ease;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
    }
    .stButton > button:hover {
        transform: scale(1.02);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
    }
    /* Primary buttons in the Airbnb coral */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #FF385C 0%, #E61E4D 100%) !important;
        color: white !important;
        border: none !important;
    }
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(135deg, #E61E4D 0%, #C2185B 100%) !important;
    }

    /* --- Tabs: bigger, bolder, with coral underline on active --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 32px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    }
    .stTabs [data-baseweb="tab"] {
        font-weight: 600 !important;
        font-size: 1rem !important;
        padding: 12px 4px !important;
    }
    .stTabs [aria-selected="true"] {
        color: #FF385C !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #FF385C !important;
        height: 3px !important;
    }

    /* --- Metric cards: subtle background --- */
    [data-testid="stMetric"] {
        background-color: rgba(255, 56, 92, 0.04);
        border-radius: 12px;
        padding: 16px;
        border: 1px solid rgba(255, 56, 92, 0.08);
    }
    [data-testid="stMetricLabel"] {
        font-weight: 600 !important;
        color: rgba(0, 0, 0, 0.6);
    }
    [data-testid="stMetricValue"] {
        font-weight: 700 !important;
        color: #222 !important;
    }

    /* --- Expanders: cleaner, rounded --- */
    .streamlit-expanderHeader {
        border-radius: 12px !important;
        font-weight: 500 !important;
    }

    /* --- Sidebar: a little more breathing room --- */
    [data-testid="stSidebar"] {
        padding-top: 1.5rem;
    }
    [data-testid="stSidebar"] .stButton > button {
        font-size: 0.9rem !important;
        padding: 0.4rem 0.8rem !important;
    }

    /* --- Success/Info/Warning alerts: softer, more rounded --- */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
    }

    /* --- Select boxes & inputs: smoother --- */
    .stSelectbox > div > div, .stTextInput > div > div > input {
        border-radius: 8px !important;
    }

    /* --- Reduce default top padding for more content above the fold --- */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 3rem !important;
        max-width: 1280px !important;
    }

    /* --- Recipe title within cards: tighter spacing --- */
    div[data-testid="stVerticalBlockBorderWrapper"] h3 {
        margin-top: 12px !important;
        margin-bottom: 4px !important;
        font-size: 1.15rem !important;
    }

    /* --- Captions: softer color --- */
    .caption, [data-testid="stCaptionContainer"] {
        color: rgba(0, 0, 0, 0.5);
    }
    </style>
    """,
    unsafe_allow_html=True,
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
    st.sidebar.markdown(
        """
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 1.4rem; font-weight: 700; margin: 0;
                       color: #222; letter-spacing: -0.01em;">
                🥦 Your Pantry
            </h2>
            <p style="color: rgba(0,0,0,0.55); font-size: 0.85rem;
                      margin: 4px 0 0 0;">
                Add what you have — we'll match recipes to it.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

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
    # Airbnb-style hero header
    st.markdown(
        """
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.5rem; font-weight: 700; letter-spacing: -0.03em;
                       margin-bottom: 8px; color: #222;">
                What's in your kitchen tonight?
            </h1>
            <p style="font-size: 1.1rem; color: rgba(0,0,0,0.6); margin-top: 0;">
                Pick ingredients from your pantry — we'll find the perfect recipes.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    pantry = get_pantry()
    diets = get_dietary_filters()

    if not pantry:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.markdown(
                """
                <div style="padding: 32px 0;">
                    <h2 style="font-size: 1.8rem; font-weight: 600;
                               color: #222; line-height: 1.2;">
                        Let's get cooking 🍳
                    </h2>
                    <p style="color: rgba(0,0,0,0.6); font-size: 1.05rem;
                              margin-top: 12px;">
                        Add some ingredients from your pantry on the left,
                        and we'll suggest recipes that match.
                    </p>
                    <p style="color: rgba(0,0,0,0.45); font-size: 0.95rem;
                              margin-top: 16px;">
                        💡 Try the quick-add staples in the sidebar to get started.
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c2:
            st.image(
                "https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800",
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

    # Friendly results header
    st.markdown(
        f"""
        <p style="font-size: 1.05rem; color: rgba(0,0,0,0.7); margin-bottom: 24px;">
            Found <strong>{len(ranked)}</strong> recipes that match your pantry ✨
        </p>
        """,
        unsafe_allow_html=True,
    )

    # --- Display recipes as cards ---
    cols_per_row = 3
    for row_start in range(0, len(ranked), cols_per_row):
        cols = st.columns(cols_per_row, gap="large")
        for i, recipe in enumerate(ranked[row_start : row_start + cols_per_row]):
            with cols[i]:
                _render_recipe_card(recipe)


def _build_detailed_lookup(recipe: dict) -> dict[str, str]:
    """
    Build a dict mapping `ingredients[i]` → its detailed text from
    `ingredients_detailed[i]`. Used to show e.g. "2 tbsp soy sauce"
    in the missing list instead of just "soy sauce".
    """
    detailed = recipe.get("ingredients_detailed", [])
    simple = recipe.get("ingredients", [])
    lookup: dict[str, str] = {}
    for i, name in enumerate(simple):
        if i < len(detailed):
            original = detailed[i].get("original") or name
            lookup[name] = original
        else:
            lookup[name] = name
    return lookup


def _render_recipe_card(recipe: dict) -> None:
    """Display a single recipe as a card."""
    with st.container(border=True):
        if recipe.get("image"):
            st.image(recipe["image"], use_container_width=True)

        # --- Compute match data first so we can use it in the title row ---
        match_pct = int(recipe["match_score"] * 100)
        used = recipe["used_ingredients"]
        missing = recipe["missing_ingredients"]

        # Pick a color for the match badge
        if match_pct >= 80:
            badge_color = "#008A05"  # green
            badge_label = "Great match"
        elif match_pct >= 50:
            badge_color = "#FF385C"  # Airbnb coral
            badge_label = "Good match"
        else:
            badge_color = "#717171"  # neutral gray
            badge_label = "Some missing"

        # --- Title + match badge in clean Airbnb style ---
        st.markdown(
            f"""
            <div style="display: flex; justify-content: space-between;
                        align-items: flex-start; gap: 8px; margin-top: 12px;">
                <h3 style="margin: 0; font-size: 1.1rem; font-weight: 600;
                           color: #222; line-height: 1.3; flex: 1;">
                    {recipe['title']}
                </h3>
                <span style="background-color: {badge_color}; color: white;
                             padding: 4px 10px; border-radius: 999px;
                             font-size: 0.8rem; font-weight: 600;
                             white-space: nowrap;">
                    {match_pct}%
                </span>
            </div>
            <p style="color: rgba(0,0,0,0.55); font-size: 0.85rem;
                      margin: 4px 0 12px 0;">
                ⏱️ {recipe.get('ready_in_minutes', 'N/A')} min  ·  🍽️ {recipe.get('servings', 'N/A')} servings  ·  {badge_label}
            </p>
            """,
            unsafe_allow_html=True,
        )

        # --- Compact metrics row ---
        c1, c2 = st.columns(2)
        c1.metric("You have", len(used))
        c2.metric("Missing", len(missing))

        if missing:
            # Use detailed text where available so the user sees "2 tbsp soy sauce"
            # instead of just "soy sauce" in the missing list.
            detailed_lookup = _build_detailed_lookup(recipe)
            with st.expander(f"🛒 Missing: {len(missing)} items"):
                for ing in missing:
                    display = detailed_lookup.get(ing, ing)
                    st.markdown(f"• {display}")

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

            # Show full ingredient list with amounts
            detailed = recipe.get("ingredients_detailed", [])
            if detailed:
                st.markdown("**Ingredients**")
                for d in detailed:
                    st.markdown(f"• {d.get('original') or d.get('name', '')}")
            elif recipe.get("ingredients"):
                # Fallback: older saved recipes might only have the simple list
                st.markdown("**Ingredients**")
                for name in recipe["ingredients"]:
                    st.markdown(f"• {name}")

            # Nutrition (per serving)
            nut = recipe.get("nutrition") or {}
            if nut and nut.get("calories"):
                st.markdown("**Nutrition per serving**")
                n1, n2, n3, n4 = st.columns(4)
                n1.metric("Calories", f"{int(nut['calories'])}")
                n2.metric("Protein", f"{int(nut.get('protein', 0))} g")
                n3.metric("Carbs", f"{int(nut.get('carbs', 0))} g")
                n4.metric("Fat", f"{int(nut.get('fat', 0))} g")

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

                    # Show ingredients with quantities
                    detailed = recipe.get("ingredients_detailed", [])
                    if detailed:
                        with st.expander(f"📋 Ingredients ({len(detailed)})"):
                            for d in detailed:
                                st.markdown(
                                    f"• {d.get('original') or d.get('name', '')}"
                                )

                    # Nutrition summary
                    nut = recipe.get("nutrition") or {}
                    if nut and nut.get("calories"):
                        st.caption(
                            f"🔥 {int(nut['calories'])} kcal  •  "
                            f"🍗 {int(nut.get('protein', 0))}g protein"
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
    st.markdown(
        """
        <div style="margin-top: 48px; padding-top: 24px;
                    border-top: 1px solid rgba(0,0,0,0.08);
                    text-align: center; color: rgba(0,0,0,0.5);
                    font-size: 0.85rem;">
            <p style="margin: 0; font-weight: 600; color: rgba(0,0,0,0.7);">
                🍳 MealMatch
            </p>
            <p style="margin: 4px 0 0 0;">
                Cook with what you have · Reduce food waste, eat better
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
