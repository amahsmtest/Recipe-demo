import os
import requests
from flask import Flask, request, render_template_string

app = Flask(__name__)

SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")  # We'll pass this from Render later

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Smart Recipe App</title>
</head>
<body>
    <h1>What's in your fridge?</h1>
    <form method="POST">
        <input type="text" name="ingredients" placeholder="e.g. chicken, rice, broccoli" size="40"/>
        <button type="submit">Find Recipes</button>
    </form>
    {% if recipes %}
        <h2>Recipes Found:</h2>
        <ul>
            {% for recipe in recipes %}
                <li>
                    <img src="{{ recipe['image'] }}" alt="image" width="100"/>
                    <a href="https://spoonacular.com/recipes/{{ recipe['title'] | replace(' ', '-') }}-{{ recipe['id'] }}" target="_blank">{{ recipe['title'] }}</a>
                </li>
            {% endfor %}
        </ul>
    {% endif %}
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    recipes = []
    if request.method == "POST":
        ingredients = request.form["ingredients"]
        api_url = f"https://api.spoonacular.com/recipes/findByIngredients"
        params = {
            "ingredients": ingredients,
            "number": 5,
            "apiKey": SPOONACULAR_API_KEY
        }
        response = requests.get(api_url, params=params)
        if response.status_code == 200:
            recipes = response.json()

    return render_template_string(HTML_TEMPLATE, recipes=recipes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
