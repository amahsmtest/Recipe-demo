from flask import Flask, request, render_template_string, send_from_directory
import requests
import os

app = Flask(__name__)

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

@app.route("/", methods=["GET", "POST"])
def index():
    recipes = []
    error = None
    ingredients = ""
    if request.method == "POST":
        ingredients = request.form["ingredients"]
        params = {
            "ingredients": ingredients,
            "number": 10,
            "apiKey": SPOONACULAR_API_KEY,
        }
        try:
            res = requests.get("https://api.spoonacular.com/recipes/findByIngredients", params=params)
            if res.status_code == 200:
                recipes = res.json()
            else:
                error = f"Error from API: {res.status_code} - {res.text}"
        except Exception as e:
            error = str(e)

    return render_template_string(HOME_TEMPLATE, recipes=recipes, ingredients=ingredients, error=error)

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    detail_url = f"https://api.spoonacular.com/recipes/{recipe_id}/information"
    params = {"apiKey": SPOONACULAR_API_KEY}
    try:
        res = requests.get(detail_url, params=params)
        if res.status_code != 200:
            return f"<h3>API Error: {res.status_code}</h3><pre>{res.text}</pre>"
        recipe = res.json()
        return render_template_string(RECIPE_DETAIL_TEMPLATE, recipe=recipe)
    except Exception as e:
        return f"<h3>Error fetching recipe details:</h3><pre>{e}</pre>"

@app.route("/shopping-list")
def shopping_list_page():
    return render_template_string(SHOPPING_LIST_TEMPLATE)

@app.route("/favorites")
def favorites_page():
    return render_template_string(FAVORITES_TEMPLATE)

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/service-worker.js')
def service_worker():
    return send_from_directory('static', 'service-worker.js')

HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Recipe App</title>
  <link rel="manifest" href="/manifest.json" />
  <style>
    :root {
      --bg-light: #f7f7f7;
      --bg-dark: #121212;
      --text-light: #222;
      --text-dark: #eee;
      --btn-primary-light: #007bff;
      --btn-primary-dark: #3399ff;
    }
    body {
      font-family: sans-serif;
      margin: 0; padding: 1rem;
      background: var(--bg-light);
      color: var(--text-light);
      transition: background 0.3s, color 0.3s;
    }
    body.dark {
      background: var(--bg-dark);
      color: var(--text-dark);
    }
    h1 { text-align: center; }
    form { text-align: center; margin-bottom: 2rem; }
    input, button {
      font-size: 1rem; padding: 0.5rem;
      border-radius: 6px; border: 1px solid #ccc;
    }
    button {
      background: var(--btn-primary-light);
      color: white; border: none;
      cursor: pointer;
      transition: background 0.3s;
    }
    button:hover {
      background: #0056b3;
    }
    body.dark button {
      background: var(--btn-primary-dark);
    }
    .recipe {
      background: white; padding: 1rem; margin: 1rem 0;
      border-radius: 8px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.1);
      transition: background 0.3s, color 0.3s;
    }
    body.dark .recipe {
      background: #222;
      color: var(--text-dark);
      box-shadow: 0 1px 6px rgba(0,0,0,0.8);
    }
    img {
      width: 100%; border-radius: 8px;
    }
    a.button {
      display: inline-block; padding: 0.5rem 1rem;
      background: var(--btn-primary-light); color: white;
      text-decoration: none; border-radius: 5px; margin-top: 0.5rem;
    }
    body.dark a.button {
      background: var(--btn-primary-dark);
    }
    nav {
      margin-bottom: 1rem;
      text-align: center;
    }
    nav button {
      margin: 0 0.3rem;
    }
  </style>
</head>
<body>
  <nav>
    <button id="darkToggle">Toggle Dark Mode</button>
    <a href="/shopping-list" class="button">🛒 Shopping List</a>
    <a href="/favorites" class="button">❤️ Favorites</a>
  </nav>

  <h1>🍽️ Smart Recipe App</h1>
  <form method="post">
    <input type="text" name="ingredients" value="{{ ingredients }}" placeholder="e.g. chicken, rice" required />
    <button type="submit">Search</button>
  </form>

  {% if error %}
    <p style="color:red;">{{ error }}</p>
  {% endif %}

  {% for recipe in recipes %}
    <div class="recipe">
      <h3>{{ recipe.title }}</h3>
      <img src="{{ recipe.image }}" alt="{{ recipe.title }}" />
      <p><strong>Used Ingredients:</strong> {{ recipe.usedIngredientCount }} | <strong>Missed:</strong> {{ recipe.missedIngredientCount }}</p>
      <form action="/recipe/{{ recipe.id }}" method="get">
        <button type="submit">Details</button>
      </form>
    </div>
  {% endfor %}

  <script>
    // Dark mode toggle with localStorage persistence
    const toggle = document.getElementById('darkToggle');
    const body = document.body;

    function applyTheme(theme) {
      if(theme === 'dark') body.classList.add('dark');
      else body.classList.remove('dark');
    }

    toggle.onclick = () => {
      let current = localStorage.getItem('theme') || 'light';
      let next = current === 'light' ? 'dark' : 'light';
      localStorage.setItem('theme', next);
      applyTheme(next);
    };

    // On load, apply saved theme
    applyTheme(localStorage.getItem('theme') || 'light');

    // Register service worker for PWA
    if ('serviceWorker' in navigator) {
      navigator.serviceWorker.register('/service-worker.js')
      .then(() => console.log('Service Worker registered'));
    }
  </script>
</body>
</html>
"""

RECIPE_DETAIL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en" >
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{{ recipe.title }}</title>
  <style>
    body {
      font-family: sans-serif; padding: 1rem; background: #fff; line-height: 1.6;
      transition: background 0.3s, color 0.3s;
    }
    body.dark {
      background: #121212;
      color: #eee;
    }
    img {
      width: 100%; border-radius: 8px;
    }
    ul {
      padding-left: 1.2em;
    }
    button {
      padding: 0.5rem; font-size: 1rem; margin: 1rem 0;
      border-radius: 6px; border: none; cursor: pointer;
      background: #28a745; color: white;
      transition: background 0.3s;
    }
    button:hover {
      background: #1e7e34;
    }
    a {
      display: inline-block; margin: 1rem 0; color: #007BFF; text-decoration: none;
    }
    body.dark button {
      background: #3ad04a;
      color: #121212;
    }
    body.dark button:hover {
      background: #289c27;
    }
  </style>
</head>
<body>
  <nav>
    <button id="darkToggle">Toggle Dark Mode</button>
    <a href="/shopping-list">🛒 Shopping List</a> |
    <a href="/favorites">❤️ Favorites</a> |
    <a href="/">← Back to Search</a>
  </nav>

  <h1>{{ recipe.title }}</h1>
  <img src="{{ recipe.image }}" alt="{{ recipe.title }}" />
  <p><strong>Ready in:</strong> {{ recipe.readyInMinutes }} min | <strong>Servings:</strong> {{ recipe.servings }}</p>

  <h2>Ingredients</h2>
  <ul id="ingredients">
    {% for item in recipe.extendedIngredients %}
      <li>{{ item.original }}</li>
    {% endfor %}
  </ul>
  <button id="addShopping">➕ Add to Shopping List</button>
  <button id="addFavorite">❤️ Save to Favorites</button>

  <h2>Instructions</h2>
  {% if recipe.instructions %}
    <p>{{ recipe.instructions | safe }}</p>
  {% else %}
    <p><em>No instructions available.</em></p>
  {% endif %}

  <h2>Nutrition Facts</h2>
  {% if recipe.nutrition and recipe.nutrition.nutrients %}
    <ul>
      {% for nutrient in recipe.nutrition.nutrients %}
        <li><strong>{{ nutrient.name }}:</strong> {{ nutrient.amount }} {{ nutrient.unit }}</li>
      {% endfor %}
    </ul>
  {% else %}
    <p><em>No nutrition information available.</em></p>
  {% endif %}

<script>
  // Dark mode toggle same as home page
  const toggle = document.getElementById('darkToggle');
  const body = document.body;

  function applyTheme(theme) {
    if(theme === 'dark') body.classList.add('dark');
    else body.classList.remove('dark');
  }

  toggle.onclick = () => {
    let current = localStorage.getItem('theme') || 'light';
    let next = current === 'light' ? 'dark' : 'light';
    localStorage.setItem('theme', next);
    applyTheme(next);
  };

  applyTheme(localStorage.getItem('theme') || 'light');

  // Shopping list add
  document.getElementById('addShopping').onclick = () => {
    const list = JSON.parse(localStorage.getItem('shoppingList') || '[]');
    const items = [...document.querySelectorAll('#ingredients li')].map(li => li.textContent);
    const newList = [...new Set([...list, ...items])];
    localStorage.setItem('shoppingList', JSON.stringify(newList));
    alert('Ingredients added to shopping list!');
  };

  // Favorites add/remove
  const favBtn = document.getElementById('addFavorite');
  const recipeId = {{ recipe.id }};
  let favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

  function updateFavButton() {
    if (favorites.includes(recipeId)) {
      favBtn.textContent = '❤️ Remove from Favorites';
    } else {
      favBtn.textContent = '❤️ Save to Favorites';
    }
  }

  favBtn.onclick = () => {
    if (favorites.includes(recipeId)) {
      favorites = favorites.filter(id => id !== recipeId);
    } else {
      favorites.push(recipeId);
    }
    localStorage.setItem('favorites', JSON.stringify(favorites));
    updateFavButton();
  };

  updateFavButton();
</script>
</body>
</html>
"""

SHOPPING_LIST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Shopping List</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; padding: 1rem; background: #fff; }
    h1 { margin-bottom: 1rem; }
    ul { padding-left: 1.2em; }
    li { margin-bottom: 0.5rem; }
    button { padding: 0.5rem; font-size: 1rem; margin-right: 0.5rem; }
  </style>
</head>
<body>
  <h1>🛒 Shopping List</h1>
  <ul id="list"></ul>
  <button onclick="clearList()">Clear</button>
  <button onclick="copyList()">Copy</button>
  <a href="/">← Back to search</a>

  <script>
    function getList() {
      return JSON.parse(localStorage.getItem("shoppingList") || "[]");
    }

    function renderList() {
      const items = getList();
      const ul = document.getElementById("list");
      ul.innerHTML = "";
      items.forEach(item => {
        const li = document.createElement("li");
        li.textContent = "• " + item;
        ul.appendChild(li);
      });
    }

    function clearList() {
      localStorage.removeItem("shoppingList");
      renderList();
    }

    function copyList() {
      const items = getList();
      navigator.clipboard.writeText(items.join("\\n")).then(() => {
        alert("Copied to clipboard!");
      });
    }

    renderList();
  </script>
</body>
</html>
"""

FAVORITES_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <title>Favorites</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
    body { font-family: sans-serif; padding: 1rem; background: #fff; }
    h1 { margin-bottom: 1rem; }
    .recipe {
      background: #f0f0f0;
      margin-bottom: 1rem;
      padding: 1rem;
      border-radius: 8px;
    }
    img {
      max-width: 100%;
      border-radius: 8px;
    }
    button {
      padding: 0.5rem;
      margin-top: 0.5rem;
      font-size: 1rem;
      background: #dc3545;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }
    a {
      display: inline-block;
      margin-top: 1rem;
      color: #007BFF;
      text-decoration: none;
    }
  </style>
</head>
<body>
  <h1>❤️ Favorites</h1>
  <div id="favorites"></div>
  <a href="/">← Back to search</a>

  <script>
    const favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
    const container = document.getElementById('favorites');

    async function fetchRecipe(id) {
      const res = await fetch('/recipe-json/' + id);
      if (!res.ok) return null;
      return await res.json();
    }

    async function loadFavorites() {
      if (favorites.length === 0) {
        container.textContent = 'No favorites saved yet.';
        return;
      }

      for (const id of favorites) {
        const recipe = await fetchRecipe(id);
        if (!recipe) continue;

        const div = document.createElement('div');
        div.className = 'recipe';

        div.innerHTML = `
          <h3>${recipe.title}</h3>
          <img src="${recipe.image}" alt="${recipe.title}" />
          <form action="/recipe/${recipe.id}" method="get">
            <button type="submit">Details</button>
          </form>
          <button onclick="removeFavorite(${recipe.id}, this)">Remove</button>
        `;
        container.appendChild(div);
      }
    }

    function removeFavorite(id, btn) {
      let favs = JSON.parse(localStorage.getItem('favorites') || '[]');
      favs = favs.filter(f => f !== id);
      localStorage.setItem('favorites', JSON.stringify(favs));
      btn.parentElement.remove();
      if (container.children.length === 0) {
        container.textContent = 'No favorites saved yet.';
      }
    }

    loadFavorites();
  </script>
</body>
</html>
"""

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
