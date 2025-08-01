from flask import Flask, request, redirect, url_for, session, render_template_string
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'  # keep for session favorites

API_KEY = os.environ.get("SPOONACULAR_API_KEY")  # Your existing env var line (left untouched)

# -------------------------
# HTML Templates (modern Tailwind + Alpine.js)
# -------------------------

HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" class="scroll-smooth dark" x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" :class="darkMode ? 'dark' : ''" x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Recipe App</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col">
  <header class="flex justify-between items-center p-4 bg-white dark:bg-gray-800 shadow sticky top-0 z-10">
    <h1 class="text-3xl font-extrabold tracking-tight">🍽️ Smart Recipe App</h1>
    <button @click="darkMode = !darkMode" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
      class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
  </header>
  <main class="flex-grow max-w-4xl mx-auto px-4 py-8 sm:py-12">
    <form method="POST" class="mb-8 flex gap-4">
      <input name="ingredients" placeholder="Enter ingredients (comma-separated)" value="{{ ingredients|e }}"
             class="flex-grow px-4 py-3 rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400" required />
      <button type="submit"
              class="bg-indigo-600 text-white px-6 py-3 rounded-lg text-lg font-semibold hover:bg-indigo-700 transition">Search</button>
    </form>
    {% if error %}
      <p class="text-red-500 mb-6">{{ error }}</p>
    {% endif %}
    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden flex flex-col">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover" />
            <div class="p-4 flex flex-col flex-grow">
              <h2 class="text-xl font-semibold mb-2">{{ recipe.title }}</h2>
              <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">Used Ingredients: {{ recipe.usedIngredientCount }} | Missed: {{ recipe.missedIngredientCount }}</p>
              <div class="mt-auto flex justify-between items-center">
                <a href="/recipe/{{ recipe.id }}" class="text-indigo-600 font-semibold hover:underline">View Details</a>
                <a href="/add_to_favorites/{{ recipe.id }}" class="text-green-600 font-semibold hover:underline text-sm">+ Favorite</a>
              </div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% endif %}
    <nav class="mt-12 flex justify-between text-lg font-semibold">
      <a href="/favorites" class="text-blue-600 hover:underline">❤️ Favorites</a>
      <a href="/shopping-list" class="text-blue-600 hover:underline">🛒 Shopping List</a>
    </nav>
  </main>
  <footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>
</body>
</html>
'''

RECIPE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" :class="darkMode ? 'dark' : ''" x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ recipe.title|e }}</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col px-6 py-8">
  <header class="flex justify-between items-center mb-6">
    <h1 class="text-4xl font-extrabold">{{ recipe.title }}</h1>
    <button @click="darkMode = !darkMode" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
      class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
  </header>
  <main class="max-w-3xl mx-auto flex-grow">
    <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="rounded-lg shadow mb-8 w-full max-h-96 object-cover" />
    <section class="mb-8">
      <h2 class="text-2xl font-semibold mb-3">Ingredients</h2>
      <ul class="list-disc list-inside space-y-1 text-lg">
        {% for ing in recipe.extendedIngredients %}
          <li>{{ ing.original }}</li>
        {% endfor %}
      </ul>
    </section>
    <section class="mb-8">
      <h2 class="text-2xl font-semibold mb-3">Instructions</h2>
      {% if recipe.instructions %}
        <div class="prose dark:prose-invert max-w-none text-lg" x-html="`{{ recipe.instructions | replace('\\n', '<br>')|replace('\r', '')|replace("`", '&#96;') }}`"></div>
      {% else %}
        <p class="italic text-gray-500 dark:text-gray-400">No instructions available.</p>
      {% endif %}
    </section>
    <a href="/" class="inline-block text-blue-600 hover:underline font-semibold mb-8">← Back to Search</a>
  </main>
  <footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>
</body>
</html>
'''

FAVORITES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="{ darkMode: localStorage.getItem('darkMode') === 'true' }" :class="darkMode ? 'dark' : ''" x-init="$watch('darkMode', val => localStorage.setItem('darkMode', val))">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Favorites - Smart Recipe App</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
</head>
<body class="bg-white dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col px-6 py-8">
  <header class="flex justify-between items-center mb-8">
    <h1 class="text-4xl font-extrabold">❤️ Your Favorite Recipes</h1>
    <button @click="darkMode = !darkMode" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
      class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
  </header>
  <main class="flex-grow max-w-4xl mx-auto">
    {% if recipes %}
      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
        {% for recipe in recipes %}
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow overflow-hidden flex flex-col">
            <img src="{{ recipe.image }}" alt="{{ recipe.title }}" class="w-full h-48 object-cover" />
            <div class="p-4 flex flex-col flex-grow">
              <h2 class="text-xl font-semibold mb-2">{{ recipe.title }}</h2>
              <div class="mt-auto flex justify-between items-center">
                <a href="/recipe/{{ recipe.id }}" class="text-indigo-600 font-semibold hover:underline">View Details</a>
                <a href="/remove_from_favorites/{{ recipe.id }}" class="text-red-600 font-semibold hover:underline text-sm">Remove</a>
              </div>
            </div>
          </div>
        {% endfor %}
      </div>
    {% else %}
      <p class="text-center text-gray-500 dark:text-gray-400 text-lg">You have no favorites yet.</p>
    {% endif %}
    <nav class="mt-12 text-center">
      <a href="/" class="text-blue-600 hover:underline font-semibold">← Back to Home</a>
    </nav>
  </main>
  <footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>
</body>
</html>
'''

SHOPPING_LIST_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="shopApp()" :class="darkMode ? 'dark' : ''" x-init="init()">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Shopping List - Smart Recipe App</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
  <style>
    .dark ::-webkit-scrollbar {
      width: 8px;
    }
    .dark ::-webkit-scrollbar-thumb {
      background-color: #555;
      border-radius: 4px;
    }
  </style>
</head>
<body class="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100 min-h-screen flex flex-col">

<header class="flex justify-between items-center p-4 bg-white dark:bg-gray-800 shadow sticky top-0 z-10">
  <h1 class="text-xl font-extrabold tracking-tight">🛒 Shopping List</h1>
  <button @click="toggleDark()" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
    class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
</header>

<main class="flex-grow max-w-3xl mx-auto px-4 py-6 sm:py-12">
  <template x-if="items.length === 0">
    <p class="text-center text-gray-500 dark:text-gray-400 mt-12 text-lg">Your shopping list is empty.</p>
  </template>
  <ul class="list-disc list-inside space-y-2" x-show="items.length > 0" tabindex="0">
    <template x-for="(item, idx) in items" :key="idx">
      <li class="flex justify-between items-center rounded bg-white dark:bg-gray-800 p-3 shadow">
        <span x-text="item"></span>
        <button @click="removeItem(idx)" aria-label="Remove item" 
          class="text-red-600 hover:text-red-400 focus:outline-none text-lg leading-none">×</button>
      </li>
    </template>
  </ul>

  <form @submit.prevent="addItem" class="mt-6 flex gap-3">
    <input type="text" x-model="newItem" placeholder="Add new item" required
      class="flex-grow rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-2 focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400 text-lg" />
    <button type="submit" 
      class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg px-6 py-2 transition">Add</button>
  </form>

  <nav class="mt-12 flex justify-center">
    <a href="/" class="text-indigo-600 hover:underline font-semibold focus:outline-none">← Back to Home</a>
  </nav>
</main>

<footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>

<script>
  function shopApp() {
    return {
      darkMode: false,
      items: JSON.parse(localStorage.getItem('shoppingList') || '[]'),
      newItem: '',
      init() {
        this.darkMode = localStorage.getItem('darkMode') === 'true';
      },
      toggleDark() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
      },
      addItem() {
        if (!this.newItem.trim()) return;
        this.items.push(this.newItem.trim());
        localStorage.setItem('shoppingList', JSON.stringify(this.items));
        this.newItem = '';
      },
      removeItem(index) {
        this.items.splice(index, 1);
        localStorage.setItem('shoppingList', JSON.stringify(this.items));
      }
    }
  }
</script>
</body>
</html>
'''

# -------------------------
# Flask Routes
# -------------------------

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
            error = f"Error fetching recipes: {str(e)}"
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
        return f"<h3>Error fetching recipe details:</h3><pre>{e}</pre>", 500
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
            pass  # skip if error
    return render_template_string(FAVORITES_TEMPLATE, recipes=recipes)

@app.route('/shopping-list')
def shopping_list_page():
    # Shopping list is stored in browser localStorage, so server just renders page
    return render_template_string(SHOPPING_LIST_TEMPLATE)

# -------------------------
# Run app
# -------------------------

if __name__ == "__main__":
    app.run(debug=True)
