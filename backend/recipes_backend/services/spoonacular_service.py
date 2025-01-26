import requests
import os

API_KEY = os.getenv("SPOONACULAR_API_KEY")

def fetch_recipes_by_ingredients(ingredients):
    url = "https://api.spoonacular.com/recipes/findByIngredients"
    params = {
        "ingredients": ",".join(ingredients),
        "number": 10,
        "apiKey": API_KEY
    }

    response = requests.get(url, params=params)
    response.raise_for_status() 
    return response.json()
