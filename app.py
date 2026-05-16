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
from api_client import RecipeProvider, analyze_fridge_image
from state import init_session_state, get_pantry, add_to_pantry, remove_from_pantry
from state import get_saved_recipes, save_recipe, unsave_recipe
from state import get_shopping_list, add_to_shopping_list, clear_shopping_list
from state import get_dietary_filters, set_dietary_filters
import meal_planner as mp

st.set_page_config(
    page_title="MealMatch — Cook with what you have",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
    <style>
    html, body, [class*="css"] { font-family: 'Circular', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    h1 { font-weight: 700 !important; letter-spacing: -0.02em; }
    h2, h3 { font-weight: 600 !important; letter-spacing: -0.01em; }
    .stImage > img { border-radius: 16px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); transition: transform 0.25s ease, box-shadow 0.25s ease; }
    .stImage > img:hover { transform: translateY(-2px); box-shadow: 0 8px 24px rgba(0,0,0,0.12); }
    div[data-testid="stVerticalBlockBorderWrapper"] { border-radius: 16px !important; border: 1px solid rgba(0,0,0,0.06) !important; box-shadow: 0 2px 8px rgba(0,0,0,0.04); padding: 16px !important; transition: transform 0.25s ease, box-shadow 0.25s ease; }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover { box-shadow: 0 12px 28px rgba(0,0,0,0.10); transform: translateY(-4px); }
    .stButton > button { border-radius: 8px !important; font-weight: 600 !important; padding: 0.5rem 1.2rem !important; transition: all 0.2s ease; border: 1px solid rgba(0,0,0,0.08) !important; }
    .stButton > button[kind="primary"] { background: linear-gradient(135deg, #FF385C 0%, #E61E4D 100%) !important; color: white !important; border: none !important; }
    .stTabs [data-baseweb="tab-list"] { gap: 32px; border-bottom: 1px solid rgba(0,0,0,0.08); }
    .stTabs [data-baseweb="tab"] { font-weight: 600 !important; font-size: 1rem !important; padding: 12px 4px !important; }
    .stTabs [aria-selected="true"] { color: #FF385C !important; }
    .stTabs [data-baseweb="tab-highlight"] { background-color: #FF385C !important; height: 3px !important; }
    [data-testid="stMetric"] { background-color: rgba(255,56,92,0.04); border-radius: 12px; padding: 16px; border: 1px solid rgba(255,56,92,0.08); }
    .block-container { padding-top: 2rem !important; padding-bottom: 3rem !important; max-width: 1280px !important; }
    </style>
""", unsafe_allow_html=True)

init_session_state()
mp.init_meal_plan()

@st.cache_resource
def get_provider() -> RecipeProvider:
    return RecipeProvider()

provider = get_provider()


def render_sidebar() -> None:
    st.sidebar.markdown("""
        <div style="margin-bottom: 16px;">
            <h2 style="font-size: 1.4rem; font-weight: 700; margin: 0; color: #222;">🥦 Your Pantry</h2>
            <p style="color: rgba(0,0,0,0.55); font-size: 0.85rem; margin: 4px 0 0 0;">Add what you have — we'll match recipes to it.</p>
        </div>
    """, unsafe_allow_html=True)

    with st.sidebar.form("add_ingredient_form", clear_on_submit=True):
        new_ing = st.text_input("Add ingredient", placeholder="e.g. chicken, tomato, basil")
        submitted = st.form_submit_button("➕ Add", use_container_width=True)
        if submitted and new_ing.strip():
            normalized = normalize_ingredient(new_ing)
            add_to_pantry(normalized)
            st.toast(f"Added: {normalized}", icon="✅")

    st.sidebar.markdown("**Quick add staples**")
    cols = st.sidebar.columns(2)
    for i, ing in enumerate(suggest_ingredients()):
        if cols[i % 2].button(ing, key=f"quick_{ing}", use_container_width=True):
            add_to_pantry(ing)
            st.rerun()

    st.sidebar.divider()
    pantry = get_pantry()
    st.sidebar.markdown(f"**In your pantry ({len(pantry)})**")
    if not pantry:
        st.sidebar.info("Your pantry is empty.")
    else:
        for ing in sorted(pantry):
            c1, c2 = st.sidebar.columns([4, 1])
            c1.markdown(f"• {ing}")
            if c2.button("✕", key=f"rm_{ing}"):
                remove_from_pantry(ing)
                st.rerun()
        if st.sidebar.button("🗑️ Clear all", use_container_width=True):
            for ing in list(pantry):
                remove_from_pantry(ing)
            st.rerun()

    st.sidebar.divider()
    st.sidebar.markdown("**Dietary preferences**")
    diets = ["vegetarian", "vegan", "gluten-free", "dairy-free", "low-carb"]
    selected = st.sidebar.multiselect("Restrictions", diets, default=get_dietary_filters(), label_visibility="collapsed")
    set_dietary_filters(selected)


def page_discover() -> None:
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #222;">What's in your kitchen tonight?</h1>
            <p style="font-size: 1.1rem; color: rgba(0,0,0,0.6);">Pick ingredients from your pantry — we'll find the perfect recipes.</p>
        </div>
    """, unsafe_allow_html=True)

    pantry = get_pantry()
    diets = get_dietary_filters()

    if not pantry:
        c1, c2 = st.columns([2, 3])
        with c1:
            st.markdown("""
                <div style="padding: 32px 0;">
                    <h2 style="font-size: 1.8rem; font-weight: 600; color: #222;">Let's get cooking 🍳</h2>
                    <p style="color: rgba(0,0,0,0.6); font-size: 1.05rem; margin-top: 12px;">Add some ingredients from your pantry on the left.</p>
                </div>
            """, unsafe_allow_html=True)
        with c2:
            st.image("https://images.unsplash.com/photo-1490645935967-10de6ba17061?w=800", use_container_width=True)
        return

    with st.spinner("Finding recipes..."):
        recipes = provider.search_recipes(pantry=list(pantry), diets=diets, limit=30)

    if not recipes:
        st.error("No recipes found. Try adding more ingredients.")
        return

    ranked = rank_recipes(recipes, pantry=pantry)
    st.markdown(f"<p style='color:rgba(0,0,0,0.7);margin-bottom:24px;'>Found <strong>{len(ranked)}</strong> recipes ✨</p>", unsafe_allow_html=True)

    for row_start in range(0, len(ranked), 3):
        cols = st.columns(3, gap="large")
        for i, recipe in enumerate(ranked[row_start:row_start+3]):
            with cols[i]:
                _render_recipe_card(recipe)


def _build_detailed_lookup(recipe: dict) -> dict:
    detailed = recipe.get("ingredients_detailed", [])
    simple = recipe.get("ingredients", [])
    lookup = {}
    for i, name in enumerate(simple):
        lookup[name] = detailed[i].get("original") or name if i < len(detailed) else name
    return lookup


def _render_recipe_card(recipe: dict) -> None:
    with st.container(border=True):
        if recipe.get("image"):
            st.image(recipe["image"], use_container_width=True)

        match_pct = int(recipe["match_score"] * 100)
        used = recipe["used_ingredients"]
        missing = recipe["missing_ingredients"]
        badge_color = "#008A05" if match_pct >= 80 else "#FF385C" if match_pct >= 50 else "#717171"
        badge_label = "Great match" if match_pct >= 80 else "Good match" if match_pct >= 50 else "Some missing"

        st.markdown(f"""
            <div style="display:flex;justify-content:space-between;align-items:flex-start;gap:8px;margin-top:12px;">
                <h3 style="margin:0;font-size:1.1rem;font-weight:600;color:#222;flex:1;">{recipe['title']}</h3>
                <span style="background-color:{badge_color};color:white;padding:4px 10px;border-radius:999px;font-size:0.8rem;font-weight:600;">{match_pct}%</span>
            </div>
            <p style="color:rgba(0,0,0,0.55);font-size:0.85rem;margin:4px 0 12px 0;">⏱️ {recipe.get('ready_in_minutes','N/A')} min · 🍽️ {recipe.get('servings','N/A')} servings · {badge_label}</p>
            <div style="display:flex;gap:8px;margin-bottom:12px;">
                <span style="background-color:rgba(0,138,5,0.08);padding:6px 12px;border-radius:999px;font-size:0.85rem;">✓ {len(used)} you have</span>
                <span style="background-color:rgba(0,0,0,0.04);padding:6px 12px;border-radius:999px;font-size:0.85rem;">• {len(missing)} missing</span>
            </div>
        """, unsafe_allow_html=True)

        if missing:
            lookup = _build_detailed_lookup(recipe)
            with st.expander(f"🛒 Missing: {len(missing)} items"):
                for ing in missing:
                    st.markdown(f"• {lookup.get(ing, ing)}")

        b1, b2 = st.columns(2)
        if b1.button("💾 Save", key=f"save_{recipe['id']}", use_container_width=True):
            save_recipe(recipe)
            st.toast(f"Saved: {recipe['title']}", icon="💾")
        if b2.button("🛒 Add missing", key=f"shop_{recipe['id']}", use_container_width=True, disabled=not missing):
            for ing in missing:
                add_to_shopping_list(ing)
            st.toast(f"Added {len(missing)} items", icon="🛒")

        with st.expander("📖 View recipe"):
            detailed = recipe.get("ingredients_detailed", [])
            if detailed:
                st.markdown("**Ingredients**")
                for d in detailed:
                    st.markdown(f"• {d.get('original') or d.get('name','')}")
            nut = recipe.get("nutrition") or {}
            if nut and nut.get("calories"):
                st.markdown(f"🔥 {int(nut['calories'])} kcal · 🍗 {int(nut.get('protein',0))}g protein · 🍞 {int(nut.get('carbs',0))}g carbs")
            if recipe.get("instructions"):
                st.markdown("**Instructions**")
                st.markdown(recipe["instructions"])


def page_saved() -> None:
    st.title("💾 Saved Recipes")
    saved = get_saved_recipes()
    if not saved:
        st.info("No saved recipes yet. Head to **Discover**!")
        return
    st.caption(f"**{len(saved)}** saved recipes.")
    for row_start in range(0, len(saved), 3):
        cols = st.columns(3)
        for i, recipe in enumerate(saved[row_start:row_start+3]):
            with cols[i]:
                with st.container(border=True):
                    if recipe.get("image"):
                        st.image(recipe["image"], use_container_width=True)
                    st.markdown(f"### {recipe['title']}")
                    st.caption(f"⏱️ {recipe.get('ready_in_minutes','N/A')} min • 🍽️ {recipe.get('servings','N/A')} servings")
                    if st.button("🗑️ Remove", key=f"unsave_{recipe['id']}", use_container_width=True):
                        unsave_recipe(recipe["id"])
                        st.rerun()


def page_shopping() -> None:
    st.title("🛒 Shopping List")
    items = get_shopping_list()
    if not items:
        st.info("Your shopping list is empty.")
        return
    st.caption(f"**{len(items)}** items to buy")
    consolidated = build_shopping_list(items)
    for category, ings in consolidated.items():
        st.markdown(f"### {category}")
        for ing in ings:
            st.checkbox(ing, key=f"check_{ing}")
    st.divider()
    c1, c2 = st.columns(2)
    if c1.button("📋 Copy as text", use_container_width=True):
        st.code("\n".join(f"- {item}" for item in items), language="markdown")
    if c2.button("🗑️ Clear list", use_container_width=True, type="primary"):
        clear_shopping_list()
        st.rerun()


def page_planner() -> None:
    st.title("📅 Weekly Meal Planner")
    saved = get_saved_recipes()
    if not saved:
        st.warning("Save some recipes first in **Discover**!")
        return

    plan = mp.get_plan()
    planned = mp.planned_count()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("📋 Meals planned", f"{planned} / 21")
    missing = mp.week_missing_ingredients(get_pantry())
    c2.metric("🛒 To buy", len(missing))
    nutr = mp.week_nutrition_summary()
    c3.metric("🔥 Total kcal", f"{int(nutr['calories']):,}" if nutr["calories"] else "—")
    c4.metric("🍗 Total protein", f"{int(nutr['protein'])} g" if nutr["calories"] else "—")
    st.divider()

    recipe_options = {"— (empty) —": None}
    for r in saved:
        recipe_options[r["title"]] = r

    for day in mp.DAYS:
        st.markdown(f"### {day}")
        cols = st.columns(len(mp.MEALS))
        for col_idx, meal in enumerate(mp.MEALS):
            with cols[col_idx]:
                current = plan[day][meal]
                default_label = "— (empty) —" if current is None else current["title"]
                options_list = list(recipe_options.keys())
                if default_label not in options_list:
                    default_label = "— (empty) —"
                chosen_label = st.selectbox(meal, options_list, index=options_list.index(default_label), key=f"plan_{day}_{meal}")
                chosen_recipe = recipe_options[chosen_label]
                if chosen_recipe != current:
                    mp.set_slot(day, meal, chosen_recipe)
                    st.rerun()
                if chosen_recipe and chosen_recipe.get("image"):
                    st.image(chosen_recipe["image"], use_container_width=True)
        st.divider()


def page_fridge_scan() -> None:
    st.markdown("""
        <div style="margin-bottom: 24px;">
            <h1 style="font-size: 2.5rem; font-weight: 700; color: #222;">📷 Fridge Scan</h1>
            <p style="font-size: 1.1rem; color: rgba(0,0,0,0.6);">Upload a photo of your fridge — AI will detect what's inside.</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload fridge photo", type=["jpg", "jpeg", "png"])

    if uploaded_file:
        st.image(uploaded_file, caption="Your fridge", use_container_width=True)

        if st.button("🔍 Start AI Analysis", type="primary"):
            with st.spinner("AI is analyzing your fridge..."):
                image_bytes = uploaded_file.read()
                ingredients = analyze_fridge_image(image_bytes)
            st.session_state["fridge_ingredients"] = ingredients

        if "fridge_ingredients" in st.session_state:
            ingredients = st.session_state["fridge_ingredients"]
            st.success(f"✅ {len(ingredients)} ingredients found!")
            cols = st.columns(3)
            for i, item in enumerate(ingredients):
                cols[i % 3].markdown(f"• {item}")
            st.divider()
            if st.button("➕ Add all to Pantry", type="primary"):
                for item in ingredients:
                    add_to_pantry(item.lower().strip())
                del st.session_state["fridge_ingredients"]
                st.success("✅ All ingredients added to pantry!")
                st.rerun()
def main() -> None:
    render_sidebar()

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["🍳 Discover", "💾 Saved", "📅 Planner", "🛒 Shopping List", "📷 Fridge Scan"]
    )

    with tab1:
        page_discover()
    with tab2:
        page_saved()
    with tab3:
        page_planner()
    with tab4:
        page_shopping()
    with tab5:
        page_fridge_scan()

    st.markdown("""
        <div style="margin-top: 48px; padding-top: 24px; border-top: 1px solid rgba(0,0,0,0.08); text-align: center; color: rgba(0,0,0,0.5); font-size: 0.85rem;">
            <p style="margin: 0; font-weight: 600; color: rgba(0,0,0,0.7);">🍳 MealMatch</p>
            <p style="margin: 4px 0 0 0;">Cook with what you have · Reduce food waste, eat better</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
