from fastapi import APIRouter, HTTPException
from shared.firebase_config import db  # Firestore database instance
from ..services.spoonacular_service import fetch_recipes_by_ingredients

router = APIRouter()

@router.get("/", summary="Fetch recipes by ingredients")
async def get_recipes():
    # step 1: retrieve ingredients from Firestore
    ingredients_ref = db.collection("ingredients").stream()
    ingredients = [doc.to_dict().get("name") for doc in ingredients_ref]

    if not ingredients:
        raise HTTPException(status_code=404, detail="No ingredients found in the database")

    # step 2: fetch recipes from Spoonacular API
    try:
        recipes = fetch_recipes_by_ingredients(ingredients)
        return {"recipes": recipes}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
