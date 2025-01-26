from fastapi import APIRouter, HTTPException
from shared.firebase_config import db  # Firestore database instance
from ..services.spoonacular_service import fetch_recipes_by_ingredients
import datetime

router = APIRouter()

MAX_RECIPES = 30  # Maximum number of recipes allowed in Firestore

@router.get("/", summary="Fetch and store recipes by ingredients")
async def get_recipes():
    # Step 1: Retrieve ingredients from Firestore
    ingredients_ref = db.collection("ingredients").stream()
    ingredients = [doc.to_dict().get("name") for doc in ingredients_ref]

    if not ingredients:
        raise HTTPException(status_code=404, detail="No ingredients found in the database")

    # Step 2: Fetch recipes from Spoonacular API
    try:
        recipes = fetch_recipes_by_ingredients(ingredients)

        # Step 3: Sort recipes by `usedIngredientCount` in descending order
        sorted_recipes = sorted(recipes, key=lambda r: r.get("usedIngredientCount", 0), reverse=True)

        # Step 4: Enforce maximum recipe limit in Firestore
        recipes_ref = db.collection("recipes")
        existing_recipes = list(recipes_ref.stream())

        if len(existing_recipes) + len(sorted_recipes) > MAX_RECIPES:
            # Sort existing recipes by most used ingredients to least (or `createdAt` as a fallback)
            sorted_existing_recipes = sorted(
                existing_recipes, key=lambda x: x.to_dict().get("usedIngredientCount", 0), reverse=True
            )

            # Calculate how many recipes need to be deleted
            num_to_delete = (len(existing_recipes) + len(sorted_recipes)) - MAX_RECIPES

            # Delete the least relevant recipes
            for recipe_doc in sorted_existing_recipes[-num_to_delete:]:
                db.collection("recipes").document(recipe_doc.id).delete()

        # Step 5: Add the new recipes
        for recipe in sorted_recipes:
            recipes_ref.document(f"recipe_{recipe['id']}").set({
                **recipe,
                "createdAt": datetime.datetime.utcnow().isoformat()  # Add timestamp for reference
            })

        # Step 6: Return the stored recipes
        return {"message": "Recipes fetched, sorted by used ingredients, and stored successfully", "recipes": sorted_recipes}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching or storing recipes: {str(e)}")
