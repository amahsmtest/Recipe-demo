from flask import Flask, request, redirect, url_for, session, render_template_string
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_KEY = os.environ.get("SPOONACULAR_API_KEY")  # Leave this line untouched as requested

# HTML templates (Tailwind-styled)
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" class="scroll-smooth dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Recipe App</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-gray-50 text-gray-900 dark:bg-gray-900 dark:text-gray-100">
  <div class="max-w-4xl mx-auto px-4 py-8">
    <h1 class="text-4xl font-bold mb-6 text-center">Smart Recipe App</h1>
    <form method="POST" class="mb-6 flex gap-4">
      <input name="ingredients" placeholder="Enter ingredients (comma-separated)" value="{{ ingredients }}"
             class="flex-grow px-4 py-2 border rounded-lg dark:bg-gray-700" required />
      <button type="submit"
              class="bg-indigo-600 text-white px-4 py-2 rounded hover:bg-indigo-700">Search</button>
    </form>
    {% if error %}
      <p class="text-red-500 mb-4">{{ error }}</p>
    {% endif %}
    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover">
            <div class="p-4">
              <h2 class="text-lg font-semibold">{{ recipe.title }}</h2>
              <a href="/recipe/{{ recipe.id }}" class="text-indigo-600 hover:underline">View Details</a><br>
              <a href="/add_to_favorites/{{ recipe.id }}" class="text-green-600 hover:underline text-sm">Add to Favorites</a>
            </div>
          </div>
        {% endfor %}
      </div>
    {% endif %}
    <div class="mt-8 flex justify-between text-sm">
      <a href="/favorites" class="text-blue-600 hover:underline">View Favorites</a>
      <a href="/shopping-list" class="text-blue-600 hover:underline">Shopping List</a>
    </div>
  </div>
</body>
</html>
'''

RECIPE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ recipe.title }}</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-6 py-8">
  <div class="max-w-3xl mx-auto">
    <h1 class="text-3xl font-bold mb-4">{{ recipe.title }}</h1>
    <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="rounded shadow mb-6 w-full max-h-96 object-cover" />
    <h2 class="text-xl font-semibold mb-2">Ingredients</h2>
    <ul class="list-disc list-inside mb-4">
      {% for ing in recipe.extendedIngredients %}
        <li>{{ ing.original }}</li>
      {% endfor %}
    </ul>
    <h2 class="text-xl font-semibold mb-2">Instructions</h2>
    <p class="mb-6">{{ recipe.instructions|safe }}</p>
    <a href="/" class="text-blue-600 hover:underline">← Back to search</a>
  </div>
</body>
</html>
'''
FAVORITES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Favorites</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-6 py-8">
  <div class="max-w-4xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Your Favorite Recipes</h1>
    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover">
            <div class="p-4">
              <h2 class="text-lg font-semibold">{{ recipe.title }}</h2>
              <a href="/recipe/{{ recipe.id }}" class="text-indigo-600 hover:underline">View Details</a><br>
              <a href="/remove_from_favorites/{{ recipe.id }}" class="text-red-600 hover:underline text-sm">Remove</a>
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-gray-500">No favorites yet.</p>
    {% endif %}
    <div class="mt-8">
      <a href="/" class="text-blue-600 hover:underline">← Back to Home</a>
    </div>
  </div>
</body>
</html>
'''

SHOPPING_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Shopping List</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@3.3.2/dist/tailwind.min.css" rel="stylesheet">
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 px-6 py-8">
  <div class="max-w-2xl mx-auto">
    <h1 class="text-3xl font-bold mb-6">Your Shopping List</h1>
    {% if items %}
      <ul class="list-disc list-inside space-y-1">
        {% for item in items %}
          <li>{{ item }}</li>
        {% endfor %}
      </ul>
    {% else %}
      <p class="text-gray-500">Your list is empty.</p>
    {% endif %}
    <div class="mt-8">
      <a href="/" class="text-blue-600 hover:underline">← Back to Home</a>
    </div>
  </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    recipes = []
    error = None
    ingredients = ""
    if request.method == 'POST':
        ingredients = request.form['ingredients']
        try:
            response = requests.get(
                f"https://api.spoonacular.com/recipes/findByIngredients",
                params={"ingredients": ingredients, "number": 10, "apiKey": API_KEY}
            )
            response.raise_for_status()
            recipes = response.json()
        except Exception as e:
            error = f"Error: {str(e)}"
    return render_template_string(HOME_TEMPLATE, recipes=recipes, error=error, ingredients=ingredients)

@app.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    response = requests.get(
        f"https://api.spoonacular.com/recipes/{recipe_id}/information",
        params={"includeNutrition": "false", "apiKey": API_KEY}
    )
    recipe = response.json()
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
        res = requests.get(
            f"https://api.spoonacular.com/recipes/{recipe_id}/information",
            params={"apiKey": API_KEY}
        )
        recipes.append(res.json())
    return render_template_string(FAVORITES_TEMPLATE, recipes=recipes)
    # New API endpoint to serve recipe JSON data for favorites page
@app.route("/recipe-json/<int:recipe_id>")
def recipe_json(recipe_id):
    detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    try:
        res = requests.get(detail_url, params=params)
        if res.status_code != 200:
            return {}, 404
        return res.json()
    except:
        return {}, 500

if __name__ == "__main__":
    app.run(debug=True)
