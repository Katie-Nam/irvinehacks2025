from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from shared.firebase_config import db  # Firestore database instance
from typing import Optional

router = APIRouter()

# Define the User model
class UserProfile(BaseModel):
    name: str
    phone: str
    email: EmailStr
    dietary_restrictions: Optional[list[str]] = []  # Optional field

# Create a new user profile
@router.post("/user", summary="Create a new user profile")
async def create_user_profile(user: UserProfile):
    try:
        # Firestore collection for user profiles
        users_ref = db.collection("users")
        existing_user = users_ref.where("email", "==", user.email).get()

        # Check if the user already exists
        if existing_user:
            raise HTTPException(status_code=400, detail="User with this email already exists")

        # Add user profile to Firestore
        users_ref.add(user.dict())
        return {"message": "User profile created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating user profile: {str(e)}")

# Retrieve a user profile by email
@router.get("/user/{email}", summary="Get user profile by email")
async def get_user_profile(email: str):
    try:
        users_ref = db.collection("users")
        user_docs = users_ref.where("email", "==", email).get()

        if not user_docs:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the first matching user (assuming email is unique)
        user_data = user_docs[0].to_dict()
        return {"user": user_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving user profile: {str(e)}")

# Update an existing user profile
@router.put("/user/{email}", summary="Update user profile by email")
async def update_user_profile(email: str, updated_user: UserProfile):
    try:
        users_ref = db.collection("users")
        user_docs = users_ref.where("email", "==", email).get()

        if not user_docs:
            raise HTTPException(status_code=404, detail="User not found")

        # Update the user profile in Firestore
        user_doc = user_docs[0]
        users_ref.document(user_doc.id).set(updated_user.dict())
        return {"message": "User profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating user profile: {str(e)}")

# Delete a user profile
@router.delete("/user/{email}", summary="Delete user profile by email")
async def delete_user_profile(email: str):
    try:
        users_ref = db.collection("users")
        user_docs = users_ref.where("email", "==", email).get()

        if not user_docs:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the user profile
        user_doc = user_docs[0]
        users_ref.document(user_doc.id).delete()
        return {"message": "User profile deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting user profile: {str(e)}")
