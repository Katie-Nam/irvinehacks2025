from fastapi import FastAPI
from .routes.ingredients import router as ingredients_router
from .routes.recipes import router as recipes_router

app = FastAPI(title="Recipes Backend")

# Register the routers
app.include_router(ingredients_router, prefix="/api/ingredients", tags=["Ingredients"])
app.include_router(recipes_router, prefix="/api/recipes", tags=["Recipes"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Recipes Backend"}