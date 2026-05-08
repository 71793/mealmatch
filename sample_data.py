"""
Sample recipe data — used when no Spoonacular API key is configured.

This lets the team develop and demo without burning API quota. Each recipe
follows the same shape that the Spoonacular adapter normalizes to.
"""

SAMPLE_RECIPES: list[dict] = [
    {
        "id": 1,
        "title": "Classic Spaghetti Aglio e Olio",
        "image": "https://images.unsplash.com/photo-1621996346565-e3dbc6d3d2a5?w=600",
        "ingredients": [
            "spaghetti",
            "garlic",
            "olive oil",
            "chili pepper",
            "parsley",
            "salt",
            "black pepper",
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
    },
    {
        "id": 2,
        "title": "Quick Chicken Stir-Fry",
        "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600",
        "ingredients": [
            "chicken breast",
            "bell pepper",
            "onion",
            "garlic",
            "soy sauce",
            "ginger",
            "olive oil",
            "rice",
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
    },
    {
        "id": 3,
        "title": "Caprese Salad",
        "image": "https://images.unsplash.com/photo-1608897013039-887f21d8c804?w=600",
        "ingredients": [
            "tomato",
            "mozzarella",
            "basil",
            "olive oil",
            "salt",
            "black pepper",
        ],
        "ready_in_minutes": 10,
        "servings": 2,
        "instructions": (
            "1. Slice tomatoes and mozzarella into rounds of similar thickness.\n\n"
            "2. Layer alternating slices on a plate with basil leaves between.\n\n"
            "3. Drizzle with olive oil. Season with salt and black pepper."
        ),
        "diets": ["vegetarian", "gluten-free"],
    },
    {
        "id": 4,
        "title": "Vegetable Fried Rice",
        "image": "https://images.unsplash.com/photo-1603133872878-684f208fb84b?w=600",
        "ingredients": [
            "rice",
            "egg",
            "scallion",
            "carrot",
            "garlic",
            "soy sauce",
            "olive oil",
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
    },
    {
        "id": 5,
        "title": "Chickpea Curry",
        "image": "https://images.unsplash.com/photo-1574484284002-952d92456975?w=600",
        "ingredients": [
            "chickpeas",
            "tomato",
            "onion",
            "garlic",
            "ginger",
            "cumin",
            "paprika",
            "olive oil",
            "rice",
        ],
        "ready_in_minutes": 35,
        "servings": 4,
        "instructions": (
            "1. Sauté onion in oil until soft. Add garlic, ginger, cumin, paprika.\n\n"
            "2. Add chopped tomatoes, simmer 5 min. Add chickpeas with their liquid.\n\n"
            "3. Simmer 15-20 min until thickened. Serve over rice."
        ),
        "diets": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
    },
    {
        "id": 6,
        "title": "Avocado Toast with Egg",
        "image": "https://images.unsplash.com/photo-1525351484163-7529414344d8?w=600",
        "ingredients": [
            "bread",
            "avocado",
            "egg",
            "lemon",
            "salt",
            "black pepper",
            "chili pepper",
        ],
        "ready_in_minutes": 10,
        "servings": 1,
        "instructions": (
            "1. Toast bread until golden.\n\n"
            "2. Mash avocado with lemon juice, salt, and pepper.\n\n"
            "3. Fry or poach egg. Spread avocado on toast, top with egg and chili."
        ),
        "diets": ["vegetarian", "dairy-free"],
    },
    {
        "id": 7,
        "title": "Greek Salad",
        "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999?w=600",
        "ingredients": [
            "tomato",
            "cucumber",
            "feta",
            "olive oil",
            "onion",
            "oregano",
            "salt",
        ],
        "ready_in_minutes": 10,
        "servings": 2,
        "instructions": (
            "1. Chop tomatoes, cucumber, and onion into chunks.\n\n"
            "2. Combine in a bowl, top with crumbled feta.\n\n"
            "3. Drizzle with olive oil, sprinkle oregano and salt."
        ),
        "diets": ["vegetarian", "gluten-free"],
    },
    {
        "id": 8,
        "title": "Tomato Basil Pasta",
        "image": "https://images.unsplash.com/photo-1551183053-bf91a1d81141?w=600",
        "ingredients": [
            "pasta",
            "tomato",
            "garlic",
            "basil",
            "olive oil",
            "parmesan",
            "salt",
        ],
        "ready_in_minutes": 25,
        "servings": 2,
        "instructions": (
            "1. Boil pasta until al dente.\n\n"
            "2. Sauté garlic in oil, add diced tomatoes and simmer 10 min.\n\n"
            "3. Toss pasta with sauce, basil, and parmesan."
        ),
        "diets": ["vegetarian"],
    },
    {
        "id": 9,
        "title": "Lentil Soup",
        "image": "https://images.unsplash.com/photo-1547592180-85f173990554?w=600",
        "ingredients": [
            "lentil",
            "carrot",
            "onion",
            "celery",
            "garlic",
            "tomato",
            "olive oil",
            "cumin",
            "salt",
        ],
        "ready_in_minutes": 40,
        "servings": 4,
        "instructions": (
            "1. Sauté onion, carrot, celery, and garlic in olive oil.\n\n"
            "2. Add lentils, diced tomatoes, cumin, and 4 cups water.\n\n"
            "3. Simmer 25-30 min until lentils are tender. Season and serve."
        ),
        "diets": ["vegetarian", "vegan", "gluten-free", "dairy-free"],
    },
    {
        "id": 10,
        "title": "Shrimp Scampi",
        "image": "https://images.unsplash.com/photo-1633504581786-316c8002b1b9?w=600",
        "ingredients": [
            "shrimp",
            "garlic",
            "butter",
            "lemon",
            "parsley",
            "pasta",
            "olive oil",
            "salt",
            "black pepper",
        ],
        "ready_in_minutes": 20,
        "servings": 4,
        "instructions": (
            "1. Cook pasta until al dente.\n\n"
            "2. Sauté garlic in butter and oil. Add shrimp, cook until pink.\n\n"
            "3. Add lemon juice and parsley. Toss with pasta. Season."
        ),
        "diets": [],
    },
    {
        "id": 11,
        "title": "Veggie Frittata",
        "image": "https://images.unsplash.com/photo-1551782450-a2132b4ba21d?w=600",
        "ingredients": [
            "egg",
            "spinach",
            "cherry tomato",
            "onion",
            "feta",
            "olive oil",
            "salt",
            "black pepper",
        ],
        "ready_in_minutes": 25,
        "servings": 4,
        "instructions": (
            "1. Beat eggs with salt and pepper.\n\n"
            "2. Sauté onion, spinach, and tomatoes in oven-safe pan.\n\n"
            "3. Pour in eggs, top with feta, finish under broiler 5 min."
        ),
        "diets": ["vegetarian", "gluten-free"],
    },
    {
        "id": 12,
        "title": "Beef Tacos",
        "image": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=600",
        "ingredients": [
            "ground beef",
            "onion",
            "garlic",
            "cumin",
            "paprika",
            "tomato",
            "lettuce",
            "cheese",
            "tortilla",
        ],
        "ready_in_minutes": 25,
        "servings": 4,
        "instructions": (
            "1. Brown ground beef with onion and garlic.\n\n"
            "2. Add cumin, paprika, and diced tomato. Simmer 5 min.\n\n"
            "3. Serve in warm tortillas with lettuce and cheese."
        ),
        "diets": [],
    },
]
