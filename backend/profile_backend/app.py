from fastapi import FastAPI
from .routes.users import router as users_router

app = FastAPI(title="Profile Backend")

# Include user routes
app.include_router(users_router, prefix="/api/users", tags=["Users"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Profile Backend"}
