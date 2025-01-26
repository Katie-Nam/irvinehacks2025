from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from shared.firebase_config import db  # Firestore instance

router = APIRouter()

# Define the request model for storing ingredients
class IngredientsRequest(BaseModel):
    ingredients: list[str]

@router.post("/store-ingredients", summary="Store user-provided ingredients in Firestore")
async def store_ingredients(ingredients_request: IngredientsRequest):
    try:
        # Firestore collection for storing ingredients
        ingredients_ref = db.collection("ingredients")

        # Add each ingredient as a new document
        for ingredient in ingredients_request.ingredients:
            ingredients_ref.add({"name": ingredient})

        return {"message": "Ingredients successfully stored in the database"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error storing ingredients: {str(e)}")
