import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Smart Recipe App</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen;
            padding: 20px;
            background-color: #fafafa;
            color: #333;
            transition: background 0.3s, color 0.3s;
        }

        @media (prefers-color-scheme: dark) {
            body {
                background-color: #1c1c1c;
                color: #f0f0f0;
            }
            input, select, button {
                background-color: #333;
                color: #fff;
                border: 1px solid #666;
            }
            .recipe {
                background-color: #2a2a2a;
            }
        }

        h1, h2 {
            text-align: center;
        }

        form {
            max-width: 500px;
            margin: auto;
            background-color: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        input, select, button {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            margin-top: 10px;
            border-radius: 6px;
            border: 1px solid #ccc;
        }

        button {
            background-color: #28a745;
            color: white;
            border: none;
        }

        button:hover {
            background-color: #218838;
        }

        .recipe {
            background-color: #fff;
            margin: 15px auto;
            padding: 15px;
            border-radius: 10px;
            max-width: 500px;
            box-shadow: 0 2px 6px rgba(0,0,0,0.1);
        }

        .recipe img {
            width: 100%;
            border-radius: 10px;
        }

        .badge {
            display: inline-block;
            background-color: #007BFF;
            color: white;
            padding: 4px 8px;
            margin: 3px 4px 3px 0;
            border-radius: 12px;
            font-size: 12px;
        }

        .button-fav {
            background-color: #ffc107;
            color: black;
            border: none;
            padding: 5px 10px;
            border-radius: 5px;
            margin-top: 8px;
            cursor: pointer;
        }

        #loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }

        #recent {
            max-width: 500px;
            margin: 10px auto;
            text-align: center;
        }

        #recent button {
            width: auto;
            margin: 5px;
            padding: 6px 12px;
        }

        @media (max-width: 600px) {
            body {
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <h1>Smart Recipe App</h1>

    <form method="POST" id="recipeForm">
        <label>Ingredients (comma-separated):</label>
        <input type="text" name="ingredients" id="ingredients" placeholder="e.g. eggs, rice, tomato">

        <label>Diet:</label>
        <select name="diet" id="diet">
            <option value="">Any</option>
            <option value="vegetarian">Vegetarian</option>
            <option value="vegan">Vegan</option>
            <option value="gluten free">Gluten Free</option>
            <option value="ketogenic">Ketogenic</option>
        </select>

        <label>Max Cook Time (mins):</label>
        <input type="number" name="max_time" id="max_time" min="0">

        <button type="submit">Search Recipes</button>
    </form>

    <div id="loading">🔄 Loading recipes...</div>

    <div id="recent">
        <h3>Recent Searches</h3>
        <div id="recentButtons"></div>
    </div>

    {% if recipes %}
        <h2>Results</h2>
        {% for r in recipes %}
            <div class="recipe">
                <h3>{{ r['title'] }}</h3>
                <img src="{{ r['image'] }}">
                <p><strong>Ready in:</strong> {{ r['readyInMinutes'] }} mins</p>

                {% if r['diets'] %}
                    {% for d in r['diets'] %}
                        <span class="badge">{{ d }}</span>
                    {% endfor %}
                {% endif %}

                {% if r['dishTypes'] %}
                    {% for d in r['dishTypes'] %}
                        <span class="badge">{{ d }}</span>
                    {% endfor %}
                {% endif %}

                <strong>Ingredients:</strong>
                <ul>
                    {% for ing in r['extendedIngredients'] %}
                        <li>{{ ing['original'] }}</li>
                    {% endfor %}
                </ul>

                <a href="{{ r['sourceUrl'] }}" target="_blank">View Full Recipe</a><br>
                <button class="button-fav" onclick="saveFavorite('{{ r['title'] | escape }}', '{{ r['sourceUrl'] | escape }}')">⭐ Save to Favorites</button>
            </div>
        {% endfor %}
    {% endif %}

    <script>
        const form = document.getElementById('recipeForm');
        const loading = document.getElementById('loading');
        const ingredientsInput = document.getElementById('ingredients');
        const dietSelect = document.getElementById('diet');
        const timeInput = document.getElementById('max_time');

        form.addEventListener('submit', () => {
            loading.style.display = 'block';
            saveRecentSearch();
        });

        function saveFavorite(title, url) {
            const favs = JSON.parse(localStorage.getItem("favorites") || "[]");
            favs.push({ title, url });
            localStorage.setItem("favorites", JSON.stringify(favs));
            alert("Recipe saved to favorites!");
        }

        function saveRecentSearch() {
            const ing = ingredientsInput.value.trim();
            const diet = dietSelect.value;
            const time = timeInput.value;
            const entry = `${ing}|${diet}|${time}`;
            let recent = JSON.parse(localStorage.getItem("recent") || "[]");
            if (!recent.includes(entry)) {
                recent.unshift(entry);
                if (recent.length > 3) recent.pop();
                localStorage.setItem("recent", JSON.stringify(recent));
            }
        }

        function loadRecentButtons() {
            const recent = JSON.parse(localStorage.getItem("recent") || "[]");
            const container = document.getElementById("recentButtons");
            recent.forEach(entry => {
                const [ing, diet, time] = entry.split("|");
                const btn = document.createElement("button");
                btn.textContent = `${ing} ${diet} ${time}min`;
                btn.onclick = () => {
                    ingredientsInput.value = ing;
                    dietSelect.value = diet;
                    timeInput.value = time;
                    form.submit();
                };
                container.appendChild(btn);
            });
        }

        loadRecentButtons();
    </script>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    recipes = []
    if request.method == "POST":
        ingredients = request.form["ingredients"]
        diet = request.form.get("diet", "")
        max_time = request.form.get("max_time", "")

        search_url = "https://api.spoonacular.com/recipes/complexSearch"
        search_params = {
            "apiKey": SPOONACULAR_API_KEY,
            "includeIngredients": ingredients,
            "addRecipeInformation": "true",
            "number": 5
        }
        if diet:
            search_params["diet"] = diet
        if max_time:
            search_params["maxReadyTime"] = max_time

        res = requests.get(search_url, params=search_params)
        if res.status_code == 200:
            data = res.json()
            recipes = data.get("results", [])

    return render_template_string(HTML_TEMPLATE, recipes=recipes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
