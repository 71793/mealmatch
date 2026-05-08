# MealMatch 🍳

Cook with what you already have. MealMatch suggests recipes based on the
ingredients in your pantry, ranks them by how well they match, generates
shopping lists for the missing items, and respects your dietary preferences.

## Project structure

```
mealmatch/
├── app.py             # Streamlit UI + page routing
├── recipe_engine.py   # Recipe ranking & shopping-list logic
├── ingredients.py     # Ingredient normalization (synonyms, modifiers)
├── api_client.py      # Spoonacular & Unsplash API client
├── state.py           # Session state wrapper
├── sample_data.py     # Local recipe dataset (offline mode)
└── requirements.txt
```

This split lets your team work in parallel:

- **Frontend / UX** → `app.py`
- **Matching engine** → `recipe_engine.py` + `ingredients.py`
- **API integration** → `api_client.py`
- **Data / content** → `sample_data.py` (extend with more recipes)

## Run it locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. (optional) Set API keys for live recipe data
export SPOONACULAR_API_KEY=your_key_here
export UNSPLASH_ACCESS_KEY=your_key_here

# 3. Launch
streamlit run app.py
```

The app runs fully **offline** without API keys — it falls back to the
12-recipe sample dataset, which is plenty for development and demos.

## What's where

### `ingredients.py`
The "scallion vs. green onion" problem. Lower-cases, strips modifiers
(*fresh*, *chopped*, *diced* …), runs synonym lookup, and singularizes.
Extend `SYNONYMS` and `MODIFIERS` as you discover new edge cases. For
production, swap the simple substring match in `ingredients_match()`
for a fuzzy matcher (`rapidfuzz`) or embeddings.

### `recipe_engine.py`
Ranks recipes by a weighted score:

```
score = 0.70 * coverage   (% of recipe ingredients you have)
      + 0.20 * usage      (% of pantry the recipe uses — burns the spinach!)
      + 0.10 * simplicity (mild bonus for short recipes)
```

Tweak the weights at the top of the file to change behaviour.

### `api_client.py`
Spoonacular's `findByIngredients` + `informationBulk` endpoints, plus an
Unsplash fallback for missing images. All API failures are caught and the
app falls back to local data — so the UI never breaks on a 429 / network
hiccup.

### `state.py`
Single source of truth for `pantry`, `saved_recipes`, `shopping_list`,
`dietary_filters`. Centralizing the session-state keys keeps the UI
code clean and makes it easy to swap in persistent storage later
(SQLite / Firebase / whatever).

## Roadmap ideas

- Persist pantry across sessions (SQLite or a `.json` per user)
- Smarter ingredient matching with `rapidfuzz` or sentence-transformers
- Expiration-date tracking → prioritize recipes using soon-to-expire items
- Unit conversion service (metric ↔ imperial) for international users
- Meal planner: drag recipes onto a weekly calendar
- Nutrition aggregation across the week
