from flask import Flask, request, redirect, url_for, session, render_template_string
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_KEY = os.environ.get("SPOONACULAR_API_KEY")  # Leave this line untouched as requested

# ----------- HTML TEMPLATES WITH TAILWIND & ALPINE DARK MODE -----------

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" 
      x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="darkMode ? 'dark' : ''" 
      x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Recipe App</title>
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    // Instant dark mode flash fix before Alpine loads
    if(localStorage.getItem('darkMode') === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  </script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col">
  <div class="max-w-5xl mx-auto px-4 py-8 flex-grow">
    <header class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-extrabold tracking-tight">🍽️ Smart Recipe App</h1>
      <button 
        @click="darkMode = !darkMode"
        class="rounded px-3 py-2 border border-gray-400 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        x-text="darkMode ? '🌙 Dark' : '☀️ Light'">
      </button>
    </header>

    <form method="POST" class="flex gap-4 mb-10">
      <input
        type="text"
        name="ingredients"
        value="{{ ingredients }}"
        placeholder="Enter ingredients, e.g. chicken, rice"
        required
        class="flex-grow rounded-lg border border-gray-300 dark:border-gray-700 px-4 py-2 bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:ring-2 focus:ring-indigo-500"
      />
      <button
        type="submit"
        class="bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg px-6 py-2 font-semibold transition"
      >
        Search
      </button>
    </form>

    {% if error %}
      <p class="text-red-500 mb-6">{{ error }}</p>
    {% endif %}

    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden flex flex-col">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover" />
            <div class="p-4 flex flex-col flex-grow">
              <h2 class="text-lg font-semibold mb-2">{{ recipe.title }}</h2>
              <div class="mt-auto space-x-2">
                <a href="/recipe/{{ recipe.id }}" 
                   class="inline-block text-indigo-600 hover:text-indigo-800 font-semibold transition">
                  View Details
                </a>
                <a href="/add_to_favorites/{{ recipe.id }}" 
                   class="inline-block text-green-600 hover:text-green-800 font-semibold transition text-sm">
                  + Favorites
                </a>
              </div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-gray-500 dark:text-gray-400 text-center mt-16">Try searching with some ingredients above.</p>
    {% endif %}

    <footer class="mt-16 flex justify-center gap-6 text-sm text-indigo-600">
      <a href="/favorites" class="hover:underline">❤️ Favorites</a>
      <a href="/shopping-list" class="hover:underline">🛒 Shopping List</a>
    </footer>
  </div>
</body>
</html>
'''

RECIPE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" 
      x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="darkMode ? 'dark' : ''" 
      x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ recipe.title }}</title>
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    if(localStorage.getItem('darkMode') === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  </script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen px-6 py-8">
  <div class="max-w-4xl mx-auto">
    <header class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-extrabold tracking-tight">{{ recipe.title }}</h1>
      <button 
        @click="darkMode = !darkMode"
        class="rounded px-3 py-2 border border-gray-400 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        x-text="darkMode ? '🌙 Dark' : '☀️ Light'">
      </button>
    </header>

    <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="rounded-lg shadow-lg mb-8 w-full max-h-96 object-cover" />

    <div class="mb-6">
      <h2 class="text-2xl font-semibold mb-2">Ingredients</h2>
      <ul class="list-disc list-inside space-y-1 text-lg">
        {% for ing in recipe.extendedIngredients %}
          <li>{{ ing.original }}</li>
        {% endfor %}
      </ul>
    </div>

    <div class="mb-6">
      <h2 class="text-2xl font-semibold mb-2">Instructions</h2>
      {% if recipe.instructions %}
        <p class="prose max-w-none dark:prose-invert">{{ recipe.instructions | safe }}</p>
      {% else %}
        <p class="italic text-gray-500 dark:text-gray-400">No instructions available.</p>
      {% endif %}
    </div>

    <a href="/" class="inline-block mt-6 text-indigo-600 hover:underline text-lg font-semibold">← Back to Search</a>
  </div>
</body>
</html>
'''

FAVORITES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" 
      x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="darkMode ? 'dark' : ''" 
      x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Favorites</title>
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    if(localStorage.getItem('darkMode') === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  </script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen px-6 py-8">
  <div class="max-w-5xl mx-auto">
    <header class="flex justify-between items-center mb-8">
      <h1 class="text-4xl font-extrabold tracking-tight">❤️ Your Favorite Recipes</h1>
      <button 
        @click="darkMode = !darkMode"
        class="rounded px-3 py-2 border border-gray-400 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-700 transition"
        x-text="darkMode ? '🌙 Dark' : '☀️ Light'">
      </button>
    </header>

    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden flex flex-col">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover" />
            <div class="p-4 flex flex-col flex-grow">
              <h2 class="text-lg font-semibold mb-2">{{ recipe.title }}</h2>
              <div class="mt-auto space-x-2">
                <a href="/recipe/{{ recipe.id }}" 
                   class="inline-block text-indigo-600 hover:text-indigo-800 font-semibold transition">
                  View Details
                </a>
                <a href="/remove_from_favorites/{{ recipe.id }}" 
                   class="inline-block text-red-600 hover:text-red-800 font-semibold transition text-sm">
                  Remove
                </a>
              </div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-gray-500 dark:text-gray-400 text-center mt-20">No favorite recipes yet.</p>
    {% endif %}

    <a href="/" class="inline-block mt-12 text-indigo-600 hover:underline text-lg font-semibold">← Back to Home</a>
  </div>
</body>
</html>
'''

SHOPPING_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" 
      x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" 
      :class="darkMode ? 'dark' : ''" 
      x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Shopping List</title>
  <script>
    tailwind.config = { darkMode: 'class' }
  </script>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    if(localStorage.getItem('darkMode') === 'true') {
      document.documentElement.classList.add('dark')
    } else {
      document.documentElement.classList.remove('dark')
    }
  </script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen px-6 py-8">
  <div class="max-w-2xl mx-auto">
    <h1 class="text-4xl font-extrabold mb-8">🛒 Your Shopping List</h1>

    {% if items %}
      <ul class="list-disc list-inside space-y-2 text-lg">
        {% for item in items %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p class="text-gray-500 dark:text-gray-400 italic text-center mt-20">Your shopping list is empty.</p>
    {% endif %}

    <a href="/" class="inline-block mt-12 text-indigo-600 hover:underline text-lg font-semibold">← Back to Home</a>
  </div>
</body>
</html>
'''

# ----------- ROUTES -----------

@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    error = None
    ingredients = ""
    if request.method == 'POST':
        ingredients = request.form['ingredients']
        try:
            response = requests.get(
                "https://api.spoonacular.com/recipes/findByIngredients",
                params={"ingredients": ingredients, "number": 10, "apiKey": API_KEY}
            )
            response.raise_for_status()
            recipes = response.json()
        except Exception as e:
            error = f"Error: {str(e)}"
    return render_template_string(HOME_TEMPLATE, recipes=recipes, error=error, ingredients=ingredients)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    try:
        response = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/information",
            params={"includeNutrition": "false", "apiKey": API_KEY}
        )
        response.raise_for_status()
        recipe = response.json()
    except Exception as e:
        recipe = {
            "title": "Error loading recipe",
            "extendedIngredients": [],
            "instructions": f"Could not load details: {str(e)}",
            "image": ""
        }
    return render_template_string(RECIPE_DETAIL_TEMPLATE, recipe=recipe)

@app.route('/add_to_favorites/<int:recipe_id>')
def add_to_favorites(recipe_id):
    favorites = session.get('favorites', [])
    if recipe_id not in favorites:
        favorites.append(recipe_id)
        session['favorites'] = favorites
    return redirect(url_for('index'))

@app.route('/remove_from_favorites/<int:recipe_id>')
def remove_from_favorites(recipe_id):
    favorites = session.get('favorites', [])
    if recipe_id in favorites:
        favorites.remove(recipe_id)
        session['favorites'] = favorites
    return redirect(url_for('favorites'))

@app.route('/favorites')
def favorites():
    favorites = session.get('favorites', [])
    recipes = []
    for recipe_id in favorites:
        try:
            res = requests.get(
                f"https://api.spoonacular.com/recipes/{recipe_id}/information",
                params={"apiKey": API_KEY}
            )
            res.raise_for_status()
            recipes.append(res.json())
        except:
            pass
    return render_template_string(FAVORITES_TEMPLATE, recipes=recipes)

@app.route('/shopping-list')
def shopping_list():
    items = session.get('shopping_list', [])
    return render_template_string(SHOPPING_LIST_TEMPLATE, items=items)

# Optional: add API endpoint for favorites if you want JSON for frontend (not mandatory)
@app.route("/recipe-json/<int:recipe_id>")
def recipe_json(recipe_id):
    detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": API_KEY}
    try:
        res = requests.get(detail_url, params=params)
        if res.status_code != 200:
            return {}, 404
        return res.json()
    except:
        return {}, 500

if __name__ == "__main__":
    app.run(debug=True)
