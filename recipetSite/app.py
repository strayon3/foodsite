from flask import Flask, render_template, request, jsonify
import requests
import json
from datetime import datetime
from info import key

app = Flask(__name__)

#spoontaculare API key and base url
BASE_URL = "https://api.spoonacular.com/recipes"


# File path for storing the meals of the day
RECIPES_FILE = 'meals_of_the_day.json'

# Function to read recipes from file
def read_recipes():
    try:
        with open(RECIPES_FILE, 'r') as file:
            data = json.load(file)
        return data
    except (FileNotFoundError, json.JSONDecodeError):
        return None

# Function to write recipes to file
def write_recipes(recipes):
    data = {
        "date": datetime.today().strftime('%Y-%m-%d'),
        "recipes": recipes
    }
    with open(RECIPES_FILE, 'w') as file:
        json.dump(data, file)

# Function to check if recipes are already stored for today
def get_meals_of_the_day():
    stored_data = read_recipes()
    today = datetime.today().strftime('%Y-%m-%d')

    # Check if the recipes file exists and if it's from today
    if stored_data and stored_data["date"] == today:
        return stored_data["recipes"]
    else:
        return None


#route from home page with navagation
@app.route('/')
def home():
    #read the stored json data
    stored_data = read_recipes()

    #check if we have recipes stored for today 
    if stored_data:
        #get the first recipe from the list
        first_recipe = stored_data["recipes"][0]
        return render_template("index.html", recipe = first_recipe)
    else:
        return render_template("index.html", error_message = "No meals of the day avalible yet...")

#route for meals of the day
@app.route('/meals_otd.html')
def meals_of_the_day():
    try:
        # Check if recipes are already stored for today
        recipes = get_meals_of_the_day()

        if not recipes:
            # If no recipes or the stored ones are not for today, fetch new recipes
            url = f"{BASE_URL}/random"
            params = {
                "number": 15,
                "apiKey": key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            recipes = data.get("recipes", [])

            # Store the new recipes
            write_recipes(recipes)

        # Render the template with the recipes
        return render_template("meals_otd.html", recipes=recipes)

    except requests.exceptions.RequestException as e:
        return render_template("error.html", error_message="Unable to fetch meals of the day")
    

@app.route('/random_recipe.html')
def random_recipe():
    try:
        url = f"{BASE_URL}/random"
        params = {
            "number": 1,
            "apiKey": key
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        recipe = data.get("recipes", [])[0]
        return render_template('random_recipe.html', recipe=recipe)
    except requests.exceptions.RequestException as e:
        return render_template('error.html', error_message = 'Unable to fetch random recipe sorry......')
    

#route search
@app.route('/search.html', methods = ['GET', 'POST'])
def search_recipes():
    if request.method == 'POST':
        query = request.form.get('query')
        if not query:
            return render_template('search.html',error_message = "Please enter a search")
        try:
            url = f"{BASE_URL}/complexSearch"
            params = {
                "query": query,
                "number": 15,
                "apiKey": key
            }
            response = requests.get(url, params=params)
            response.raise_for_status()
            data= response.json()
            recipes = data.get("results", [])
            return render_template('search_results.html', recipes=recipes, query=query)
        except requests.exceptions.RequestException as e:
            return render_template('error.html', error_message = "Unable to fetch search results")
    return render_template("search.html")

if __name__ == '__main__':
    app.run(debug=True)