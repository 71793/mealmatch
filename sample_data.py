"""
Sample recipe data — used when no Spoonacular API key is configured.

Each recipe carries:
    * ingredients          : list[str] used by the matching engine
    * ingredients_detailed : list[dict] with amount + unit + original for UI
    * nutrition            : per-serving values for the meal planner
"""


def _ing(name: str, amount: float, unit: str, original: str) -> dict:
    """Helper to build a detailed ingredient entry."""
    return {"name": name, "amount": amount, "unit": unit, "original": original}


SAMPLE_RECIPES: list[dict] = [
    {
        "id": 1,
        "title": "Classic Spaghetti Aglio e Olio",
        "image": "https://images.unsplash.com/photo-1621996346565-e3dbc6d3d2a5?w=600",
        "ingredients": [
            "spaghetti", "garlic", "olive oil", "chili pepper",
            "parsley", "salt", "black pepper",
        ],
        "ingredients_detailed": [
            _ing("spaghetti", 400, "g", "400 g spaghetti"),
            _ing("garlic", 6, "cloves", "6 cloves garlic, thinly sliced"),
            _ing("olive oil", 80, "ml", "80 ml extra virgin olive oil"),
            _ing("chili pepper", 1, "tsp", "1 tsp red chili flakes"),
            _ing("parsley", 1, "handful", "1 handful fresh parsley, chopped"),
            _ing("salt", 1, "tsp", "1 tsp salt"),
            _ing("black pepper", 0.5, "tsp", "½ tsp black pepper"),
        ],
        "ready_in_minutes": 20,
        "servings": 4,
        "instructions": (
            "1. Boil spaghetti in salted water until al dente.\n\n"
            "2. Meanwhile, gently heat olive oil with sliced garlic and chili until fragrant.\n\n"
            "3. Drain pasta, toss with garlic oil and chopped parsley.\n\n"
            "4. Season with salt and black pepper. Serve immediately."
        ),
        "diets": ["vegetarian", "vegan", "dairy-free"],
        "nutrition": {"calories": 480, "protein": 12, "carbs": 70, "fat": 18},
    },
    {
        "id": 2,
        "title": "Quick Chicken Stir-Fry",
        "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600",
        "ingredients": [
            "chicken breast", "bell pepper", "onion", "garlic",
            "soy sauce", "ginger", "olive oil", "rice",
        ],
        "ingredients_detailed": [
            _ing("chicken breast", 400, "g", "400 g chicken breast, sliced"),
            _ing("bell pepper", 2, "", "2 bell peppers, sliced"),
            _ing("onion", 1, "", "1 large onion, sliced"),
            _ing("garlic", 3, "cloves", "3 cloves garlic, minced"),
            _ing("soy sauce", 3, "tbsp", "3 tbsp soy sauce"),
            _ing("ginger", 1, "tbsp", "1 tbsp fresh ginger, grated"),
            _ing("olive oil", 2, "tbsp", "2 tbsp olive oil"),
            _ing("rice", 200, "g", "200 g jasmine rice"),
        ],
        "ready_in_minutes": 25,
        "servings": 2,
        "instructions": (
            "1. Cook rice according to package instructions.\n\n"
            "2. Slice chicken into thin strips. Heat oil in a wok over high heat.\n\n"
            "3. Stir-fry chicken until golden, then add garlic, ginger, onion, and pepper.\n\n"
            "4. Add soy sauce, toss to coat. Serve over rice."
        ),
        "diets": ["dairy-free"],
        "nutrition": {"calories": 620, "protein": 48, "carbs": 65, "fat": 14},
    },
    {
        "id": 3,
        "title": "Caprese Salad",
        "image": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600",
        "ingredients": [
            "tomato", "mozzarella", "basil",
            "olive oil", "salt", "black pepper",
        ],
        "ingredients_detailed": [
            _ing("tomato", 4, "", "4 large ripe tomatoes, sliced"),
            _ing("mozzarella", 250, "g", "250 g fresh mozzarella, sliced"),
            _ing("basil", 1, "bunch", "1 bunch fresh basil leaves"),
            _ing("olive oil", 3, "tbsp", "3 tbsp extra virgin olive oil"),
            _ing("salt", 0.5, "tsp", "½ tsp sea salt"),
            _ing("black pepper", 0.25, "tsp", "¼ tsp black pepper"),
        ],
        "ready_in_minutes": 10,
        "servings": 2,
        "instructions": (
            "1. Slice tomatoes and mozzarella into rounds of similar thickness.\n\n"
            "2. Layer alternating slices on a plate with basil leaves between.\n\n"
            "3. Drizzle with olive oil. Season with salt and black pepper."
        ),
        "diets": ["vegetarian", "gluten-free"],
        "nutrition": {"calories": 380, "protein": 20, "carbs": 12, "fat": 28},
    },
    {
        "id": 4,
        "title": "Vegetable Fried Rice",
        "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600",
        "ingredients": [
            "rice", "egg", "scallion", "carrot",
            "garlic", "soy sauce", "olive oil",
        ],
        "ingredients_detailed": [
            _ing("rice", 300, "g", "300 g day-old cooked rice"),
            _ing("egg", 2, "", "2 large eggs, beaten"),
            _ing("scallion", 3, "", "3 scallions, sliced"),
            _ing("carrot", 1, "", "1 carrot, finely diced"),
            _ing("garlic", 2, "cloves", "2 cloves garlic, minced"),
            _ing("soy sauce", 2, "tbsp", "2 tbsp soy sauce"),
            _ing("olive oil", 2, "tbsp", "2 tbsp vegetable or olive oil"),
        ],
        "ready_in_minutes": 20,
        "servings": 2,
        "instructions": (
            "1. Use day-old cooked rice for best texture.\n\n"
            "2. Scramble eggs in a hot wok and set aside.\n\n"
            "3. Stir-fry carrots and garlic, then add rice and break up clumps.\n\n"
            "4. Add soy sauce, scallions, and the cooked egg. Toss to combine."
        ),
        "diets": ["vegetarian", "dairy-free"],
        "nutrition": {"calories": 460, "protein": 14, "carbs": 68, "fat": 13},
    },
    {
        "id": 5,
        "title": "Chickpea Curry",
        "image": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=600",
        "ingredients": [
            "chickpeas", "tomato", "onion", "garlic", "ginger",
            "cumin", "paprika", "olive oil", "rice",
        ],
        "ingredients_detailed": [
            _ing("chickpeas", 400, "g", "1 can (400 g) chickpeas, drained"),
            _ing("tomato", 400, "g", "1 can (400 g) chopped tomatoes"),
            _ing("onion", 1, "", "1 large onion, diced"),
            _ing("garlic", 3, "cloves", "3 cloves garlic, minced"),
            _ing("ginger", 1, "tbsp", "1 tbsp fresh ginger, grated"),
            _ing("cumin", 1, "tsp", "1 tsp ground cumin"),
            _ing("paprika", 1, "tsp", "1 tsp smoked paprika"),
            _ing("olive oil", 2, "tbsp", "2 tbsp olive oil"),
            _ing("rice", 200, "g", "200 g basmati rice"),
        ],
        "ready_in_minutes": 35,
        "servings": 4,
        "instructions": (
            "1. Sauté onion in oil until soft. Add garlic, ginger, cumin, paprika.\n\n"
            "2. Add chopped tomatoes, simmer 5 min. Add chickpeas with their liquid.\n\n"
            "3. Simmer 15-20 min until thickened. Serve over rice."
        ),
        "diets": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
        "nutrition": {"calories": 420, "protein": 14, "carbs": 70, "fat": 10},
    },
    {
        "id": 6,
        "title": "Avocado Toast with Egg",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600",
        "ingredients": [
            "bread", "avocado", "egg", "lemon",
            "salt", "black pepper", "chili pepper",
        ],
        "ingredients_detailed": [
            _ing("bread", 2, "slices", "2 slices sourdough bread"),
            _ing("avocado", 1, "", "1 ripe avocado"),
            _ing("egg", 1, "", "1 large egg"),
            _ing("lemon", 0.5, "", "½ lemon, juiced"),
            _ing("salt", 0.25, "tsp", "¼ tsp salt"),
            _ing("black pepper", 0.25, "tsp", "¼ tsp black pepper"),
            _ing("chili pepper", 0.25, "tsp", "¼ tsp red chili flakes"),
        ],
        "ready_in_minutes": 10,
        "servings": 1,
        "instructions": (
            "1. Toast bread until golden.\n\n"
            "2. Mash avocado with lemon juice, salt, and pepper.\n\n"
            "3. Fry or poach egg. Spread avocado on toast, top with egg and chili."
        ),
        "diets": ["vegetarian", "dairy-free"],
        "nutrition": {"calories": 420, "protein": 16, "carbs": 35, "fat": 24},
    },
    {
        "id": 7,
        "title": "Greek Salad",
        "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600",
        "ingredients": [
            "tomato", "cucumber", "feta", "olive oil",
            "onion", "oregano", "salt",
        ],
        "ingredients_detailed": [
            _ing("tomato", 3, "", "3 large tomatoes, cut in chunks"),
            _ing("cucumber", 1, "", "1 cucumber, sliced"),
            _ing("feta", 150, "g", "150 g feta cheese, cubed"),
            _ing("olive oil", 3, "tbsp", "3 tbsp olive oil"),
            _ing("onion", 0.5, "", "½ red onion, thinly sliced"),
            _ing("oregano", 1, "tsp", "1 tsp dried oregano"),
            _ing("salt", 0.5, "tsp", "½ tsp salt"),
        ],
        "ready_in_minutes": 10,
        "servings": 2,
        "instructions": (
            "1. Chop tomatoes, cucumber, and onion into chunks.\n\n"
            "2. Combine in a bowl, top with crumbled feta.\n\n"
            "3. Drizzle with olive oil, sprinkle oregano and salt."
        ),
        "diets": ["vegetarian", "gluten-free"],
        "nutrition": {"calories": 340, "protein": 12, "carbs": 14, "fat": 26},
    },
    {
        "id": 8,
        "title": "Tomato Basil Pasta",
        "image": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600",
        "ingredients": [
            "pasta", "tomato", "garlic", "basil",
            "olive oil", "parmesan", "salt",
        ],
        "ingredients_detailed": [
            _ing("pasta", 250, "g", "250 g pasta of choice"),
            _ing("tomato", 500, "g", "500 g ripe tomatoes, diced"),
            _ing("garlic", 3, "cloves", "3 cloves garlic, minced"),
            _ing("basil", 1, "handful", "1 handful fresh basil leaves"),
            _ing("olive oil", 3, "tbsp", "3 tbsp olive oil"),
            _ing("parmesan", 50, "g", "50 g parmesan, grated"),
            _ing("salt", 0.5, "tsp", "½ tsp salt"),
        ],
        "ready_in_minutes": 25,
        "servings": 2,
        "instructions": (
            "1. Boil pasta until al dente.\n\n"
            "2. Sauté garlic in oil, add diced tomatoes and simmer 10 min.\n\n"
            "3. Toss pasta with sauce, basil, and parmesan."
        ),
        "diets": ["vegetarian"],
        "nutrition": {"calories": 540, "protein": 18, "carbs": 78, "fat": 18},
    },
    {
        "id": 9,
        "title": "Lentil Soup",
        "image": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600",
        "ingredients": [
            "lentil", "carrot", "onion", "celery", "garlic",
            "tomato", "olive oil", "cumin", "salt",
        ],
        "ingredients_detailed": [
            _ing("lentil", 250, "g", "250 g brown or green lentils"),
            _ing("carrot", 2, "", "2 carrots, diced"),
            _ing("onion", 1, "", "1 large onion, diced"),
            _ing("celery", 2, "stalks", "2 stalks celery, diced"),
            _ing("garlic", 3, "cloves", "3 cloves garlic, minced"),
            _ing("tomato", 400, "g", "1 can (400 g) chopped tomatoes"),
            _ing("olive oil", 2, "tbsp", "2 tbsp olive oil"),
            _ing("cumin", 1, "tsp", "1 tsp ground cumin"),
            _ing("salt", 1, "tsp", "1 tsp salt (or to taste)"),
        ],
        "ready_in_minutes": 40,
        "servings": 4,
        "instructions": (
            "1. Sauté onion, carrot, celery, and garlic in olive oil.\n\n"
            "2. Add lentils, diced tomatoes, cumin, and 4 cups water.\n\n"
            "3. Simmer 25-30 min until lentils are tender. Season and serve."
        ),
        "diets": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
        "nutrition": {"calories": 310, "protein": 18, "carbs": 50, "fat": 6},
    },
    {
        "id": 10,
        "title": "Shrimp Scampi",
        "image": "https://images.unsplash.com/photo-1633504581786-316c8002b1b9?w=600",
        "ingredients": [
            "shrimp", "garlic", "butter", "lemon", "parsley",
            "pasta", "olive oil", "salt", "black pepper",
        ],
        "ingredients_detailed": [
            _ing("shrimp", 400, "g", "400 g shrimp, peeled and deveined"),
            _ing("garlic", 4, "cloves", "4 cloves garlic, minced"),
            _ing("butter", 40, "g", "40 g butter"),
            _ing("lemon", 1, "", "1 lemon (zest + juice)"),
            _ing("parsley", 1, "handful", "1 handful fresh parsley, chopped"),
            _ing("pasta", 300, "g", "300 g linguine"),
            _ing("olive oil", 2, "tbsp", "2 tbsp olive oil"),
            _ing("salt", 0.5, "tsp", "½ tsp salt"),
            _ing("black pepper", 0.25, "tsp", "¼ tsp black pepper"),
        ],
        "ready_in_minutes": 20,
        "servings": 4,
        "instructions": (
            "1. Cook pasta until al dente.\n\n"
            "2. Sauté garlic in butter and oil. Add shrimp, cook until pink.\n\n"
            "3. Add lemon juice and parsley. Toss with pasta. Season."
        ),
        "diets": [],
        "nutrition": {"calories": 580, "protein": 32, "carbs": 60, "fat": 22},
    },
    {
        "id": 11,
        "title": "Veggie Frittata",
        "image": "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600",
        "ingredients": [
            "egg", "spinach", "cherry tomato", "onion",
            "feta", "olive oil", "salt", "black pepper",
        ],
        "ingredients_detailed": [
            _ing("egg", 8, "", "8 large eggs, beaten"),
            _ing("spinach", 100, "g", "100 g fresh spinach"),
            _ing("cherry tomato", 200, "g", "200 g cherry tomatoes, halved"),
            _ing("onion", 1, "", "1 small onion, diced"),
            _ing("feta", 100, "g", "100 g feta cheese, crumbled"),
            _ing("olive oil", 2, "tbsp", "2 tbsp olive oil"),
            _ing("salt", 0.5, "tsp", "½ tsp salt"),
            _ing("black pepper", 0.25, "tsp", "¼ tsp black pepper"),
        ],
        "ready_in_minutes": 25,
        "servings": 4,
        "instructions": (
            "1. Beat eggs with salt and pepper.\n\n"
            "2. Sauté onion, spinach, and tomatoes in oven-safe pan.\n\n"
            "3. Pour in eggs, top with feta, finish under broiler 5 min."
        ),
        "diets": ["vegetarian", "gluten-free"],
        "nutrition": {"calories": 320, "protein": 22, "carbs": 8, "fat": 22},
    },
    {
        "id": 12,
        "title": "Beef Tacos",
        "image": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600",
        "ingredients": [
            "ground beef", "onion", "garlic", "cumin",
            "paprika", "tomato", "lettuce", "cheese", "tortilla",
        ],
        "ingredients_detailed": [
            _ing("ground beef", 500, "g", "500 g ground beef"),
            _ing("onion", 1, "", "1 large onion, diced"),
            _ing("garlic", 2, "cloves", "2 cloves garlic, minced"),
            _ing("cumin", 1, "tsp", "1 tsp ground cumin"),
            _ing("paprika", 1, "tsp", "1 tsp smoked paprika"),
            _ing("tomato", 2, "", "2 tomatoes, diced"),
            _ing("lettuce", 1, "head", "1 small head of lettuce, shredded"),
            _ing("cheese", 100, "g", "100 g cheddar cheese, grated"),
            _ing("tortilla", 8, "", "8 small tortillas"),
        ],
        "ready_in_minutes": 25,
        "servings": 4,
        "instructions": (
            "1. Brown ground beef with onion and garlic.\n\n"
            "2. Add cumin, paprika, and diced tomato. Simmer 5 min.\n\n"
            "3. Serve in warm tortillas with lettuce and cheese."
        ),
        "diets": [],
        "nutrition": {"calories": 540, "protein": 30, "carbs": 38, "fat": 28},
    },
]
