from flask import Flask, request, render_template_string

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Recipe Generator</title>
</head>
<body>
    <h1>What's in your fridge?</h1>
    <form method="POST">
        <input type="text" name="ingredients" placeholder="e.g. eggs, milk, cheese" size="40"/>
        <button type="submit">Get Recipes</button>
    </form>
    {% if recipes %}
        <h2>Suggested Recipes</h2>
        <ul>
            {% for r in recipes %}
                <li>{{ r }}</li>
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
        ingredients = request.form["ingredients"].lower().split(",")
        ingredients = [i.strip() for i in ingredients]

        if "egg" in ingredients:
            recipes.append("Omelette")
        if "bread" in ingredients and "cheese" in ingredients:
            recipes.append("Grilled Cheese Sandwich")
        if "milk" in ingredients and "banana" in ingredients:
            recipes.append("Banana Smoothie")
        if not recipes:
            recipes.append("No matching recipes found. Try different ingredients.")

    return render_template_string(HTML_PAGE, recipes=recipes)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)