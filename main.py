from flask import Flask, request, redirect, url_for, session, render_template_string
import requests
import os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

API_KEY = os.environ.get("SPOONACULAR_API_KEY")  # Keep this line as you have it

# Modern Tailwind CSS + Alpine.js for minimal JS interactivity and reactivity
HOME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="app()" :class="darkMode ? 'dark' : ''" x-init="init()">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Smart Recipe App 2025</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script src="https://unpkg.com/alpinejs@3.x.x/dist/cdn.min.js" defer></script>
  <style>
    /* Custom scrollbar for dark mode */
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
    <h1 class="text-xl font-extrabold tracking-tight">🍳 Smart Recipe App</h1>
    <button @click="toggleDark()" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
      class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
  </header>

  <main class="flex-grow max-w-5xl mx-auto px-4 py-6 sm:py-12">

    <form @submit.prevent="search()" class="flex flex-col sm:flex-row gap-4 mb-8">
      <input type="text" x-model="ingredients" placeholder="Enter ingredients, e.g. chicken, rice"
        class="flex-grow rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 px-4 py-3 text-lg focus:outline-none focus:ring-2 focus:ring-indigo-500 dark:focus:ring-indigo-400"
        required />
      <button type="submit" 
        class="bg-indigo-600 hover:bg-indigo-700 text-white font-semibold rounded-lg px-6 py-3 transition">Search</button>
    </form>

    <template x-if="error">
      <div class="mb-6 p-4 bg-red-100 text-red-700 rounded-md" x-text="error"></div>
    </template>

    <template x-if="recipes.length === 0 && searched">
      <p class="text-center text-gray-500 dark:text-gray-400">No recipes found. Try different ingredients.</p>
    </template>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8" x-show="recipes.length > 0">
      <template x-for="recipe in recipes" :key="recipe.id">
        <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden hover:shadow-2xl transition cursor-pointer"
             @click="goToDetail(recipe.id)" tabindex="0" @keydown.enter="goToDetail(recipe.id)" >
          <img :src="recipe.image" :alt="recipe.title" class="w-full h-48 object-cover rounded-t-xl" />
          <div class="p-4">
            <h2 class="text-lg font-semibold mb-2" x-text="recipe.title"></h2>
            <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">
              Used: <span x-text="recipe.usedIngredientCount"></span>, Missed: <span x-text="recipe.missedIngredientCount"></span>
            </p>
            <button @click.stop="toggleFavorite(recipe.id)" class="text-indigo-600 hover:text-indigo-400 text-sm font-medium focus:outline-none" 
              x-text="favorites.includes(recipe.id) ? '❤️ Remove Favorite' : '🤍 Add Favorite'"></button>
          </div>
        </div>
      </template>
    </div>

    <nav class="mt-12 flex justify-center space-x-6 text-indigo-600 font-semibold">
      <a href="/favorites" class="hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded">Favorites</a>
      <a href="/shopping-list" class="hover:underline focus:outline-none focus:ring-2 focus:ring-indigo-500 rounded">Shopping List</a>
    </nav>
  </main>

  <footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>

  <script>
    function app() {
      return {
        darkMode: false,
        ingredients: '',
        recipes: [],
        error: '',
        favorites: [],
        searched: false,

        init() {
          // Load dark mode from localStorage
          this.darkMode = localStorage.getItem('darkMode') === 'true';
          // Load favorites from localStorage
          this.favorites = JSON.parse(localStorage.getItem('favorites') || '[]');

          // Optional: Load last searched ingredients from sessionStorage
          const lastIngredients = sessionStorage.getItem('lastIngredients');
          if (lastIngredients) {
            this.ingredients = lastIngredients;
            this.search();
          }
        },

        toggleDark() {
          this.darkMode = !this.darkMode;
          localStorage.setItem('darkMode', this.darkMode);
        },

        async search() {
          this.error = '';
          if (!this.ingredients.trim()) {
            this.error = 'Please enter at least one ingredient.';
            return;
          }
          try {
            const res = await fetch('/', {
              method: 'POST',
              headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
              body: new URLSearchParams({ ingredients: this.ingredients }),
            });
            if (!res.ok) throw new Error(`API error ${res.status}`);
            const text = await res.text();

            // Parse the returned HTML string to extract recipes JSON embedded
            // We will embed JSON in a script tag for easier parsing

            const parser = new DOMParser();
            const doc = parser.parseFromString(text, 'text/html');
            const jsonScript = doc.getElementById('recipes-json');
            if (!jsonScript) throw new Error('No recipe data found');
            const recipesData = JSON.parse(jsonScript.textContent);
            this.recipes = recipesData;
            this.searched = true;

            // Save last search ingredients
            sessionStorage.setItem('lastIngredients', this.ingredients);
          } catch (e) {
            this.error = e.message || 'Failed to fetch recipes';
          }
        },

        toggleFavorite(id) {
          if (this.favorites.includes(id)) {
            this.favorites = this.favorites.filter(f => f !== id);
          } else {
            this.favorites.push(id);
          }
          localStorage.setItem('favorites', JSON.stringify(this.favorites));
        },

        goToDetail(id) {
          window.location.href = `/recipe/${id}`;
        }
      }
    }
  </script>
</body>
</html>
'''

RECIPE_DETAIL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="detailApp()" :class="darkMode ? 'dark' : ''" x-init="init()">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title x-text="recipe.title"></title>
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
  <h1 class="text-xl font-extrabold tracking-tight" x-text="recipe.title"></h1>
  <button @click="toggleDark()" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
    class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
</header>

<main class="flex-grow max-w-4xl mx-auto px-4 py-6 sm:py-12 overflow-auto">
  <img :src="recipe.image" :alt="recipe.title" class="w-full rounded-xl shadow-md mb-6 max-h-96 object-cover" />
  
  <section class="mb-8">
    <h2 class="text-2xl font-semibold mb-2">Ingredients</h2>
    <ul class="list-disc list-inside space-y-1 text-lg">
      <template x-for="ing in recipe.extendedIngredients" :key="ing.id">
        <li x-text="ing.original"></li>
      </template>
    </ul>
  </section>

  <section class="mb-8">
    <h2 class="text-2xl font-semibold mb-2">Instructions</h2>
    <div class="prose dark:prose-invert max-w-none" x-html="recipe.instructions || '<em>No instructions provided.</em>'"></div>
  </section>

  <nav class="flex justify-between items-center">
    <button @click="goBack()" class="text-indigo-600 hover:underline focus:outline-none">← Back to Search</button>
    <button @click="toggleFavorite(recipe.id)" class="focus:outline-none rounded px-3 py-1 border
      dark:border-gray-600 text-indigo-600 dark:text-indigo-400 hover:bg-indigo-100 dark:hover:bg-indigo-800 transition"
      x-text="favorites.includes(recipe.id) ? '❤️ Remove Favorite' : '🤍 Add Favorite'"></button>
  </nav>
</main>

<footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>

<script>
  function detailApp() {
    return {
      darkMode: false,
      recipe: {{ recipe | tojson }},
      favorites: [],
      init() {
        this.darkMode = localStorage.getItem('darkMode') === 'true';
        this.favorites = JSON.parse(localStorage.getItem('favorites') || '[]');
      },
      toggleDark() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
      },
      toggleFavorite(id) {
        if (this.favorites.includes(id)) {
          this.favorites = this.favorites.filter(f => f !== id);
        } else {
          this.favorites.push(id);
        }
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
      },
      goBack() {
        window.history.back();
      }
    }
  }
</script>
</body>
</html>
'''

FAVORITES_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en" x-data="favApp()" :class="darkMode ? 'dark' : ''" x-init="init()">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>Favorites - Smart Recipe App</title>
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
  <h1 class="text-xl font-extrabold tracking-tight">❤️ Your Favorites</h1>
  <button @click="toggleDark()" :aria-label="darkMode ? 'Switch to light mode' : 'Switch to dark mode'" 
    class="p-2 rounded-md hover:bg-gray-300 dark:hover:bg-gray-700 transition" x-text="darkMode ? '☀️ Light' : '🌙 Dark'"></button>
</header>

<main class="flex-grow max-w-5xl mx-auto px-4 py-6 sm:py-12">
  <template x-if="favorites.length === 0">
    <p class="text-center text-gray-500 dark:text-gray-400 mt-12 text-lg">You have no favorite recipes yet.</p>
  </template>
  <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8" x-show="favorites.length > 0">
    <template x-for="recipe in favoriteRecipes" :key="recipe.id">
      <div class="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
        <img :src="recipe.image" :alt="recipe.title" class="w-full h-48 object-cover rounded-t-xl" />
        <div class="p-4">
          <h2 class="text-lg font-semibold mb-2" x-text="recipe.title"></h2>
          <button @click="removeFavorite(recipe.id)" 
            class="text-red-600 hover:text-red-400 text-sm font-medium focus:outline-none">
            Remove Favorite
          </button>
          <button @click="goToDetail(recipe.id)" 
            class="block mt-3 text-indigo-600 hover:underline text-sm focus:outline-none">
            View Details
          </button>
        </div>
      </div>
    </template>
  </div>
  <nav class="mt-12 flex justify-center">
    <a href="/" class="text-indigo-600 hover:underline font-semibold focus:outline-none">← Back to Home</a>
  </nav>
</main>

<footer class="text-center p-4 text-gray-500 text-sm select-none">© 2025 Smart Recipe App</footer>

<script>
  function favApp() {
    return {
      darkMode: false,
      favorites: JSON.parse(localStorage.getItem('favorites') || '[]'),
      favoriteRecipes: [],
      async init() {
        this.darkMode = localStorage.getItem('darkMode') === 'true';

        // Fetch recipe details for all favorites in parallel
        this.favoriteRecipes = await Promise.all(
          this.favorites.map(async (id) => {
            try {
              const res = await fetch(`/recipe-json/${id}`);
              if (!res.ok) throw new Error('Fetch failed');
              return await res.json();
            } catch {
              return null;
            }
          })
        );
        // Remove any nulls from failed fetches
        this.favoriteRecipes = this.favoriteRecipes.filter(r => r !== null);
      },
      toggleDark() {
        this.darkMode = !this.darkMode;
        localStorage.setItem('darkMode', this.darkMode);
      },
      removeFavorite(id) {
        this.favorites = this.favorites.filter(f => f !== id);
        localStorage.setItem('favorites', JSON.stringify(this.favorites));
        this.favoriteRecipes = this.favoriteRecipes.filter(r => r.id !== id);
      },
      goToDetail(id) {
        window.location.href = `/recipe/${id}`;
      }
    }
  }
</script>
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

  <form @submit.prevent="addItem" class
