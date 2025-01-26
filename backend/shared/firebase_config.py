# import firebase_admin
# from firebase_admin import credentials, firestore

# # Provide the path to your Firebase service account JSON file
# cred = credentials.Certificate("shared/.env")

# # Initialize Firebase app
# firebase_admin.initialize_app(cred)

# # Example: Initialize Firestore
# db = firestore.client()

# # Example: Add data to Firestore
# doc_ref = db.collection("users").document("user_id")
# doc_ref.set({
#     "name": "Test",
#     "email": "Test@email.com"
# })

# print("Data written to Firestore")

import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get the path to the Firebase service account key JSON file
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")

if not firebase_key_path:
    raise ValueError("FIREBASE_KEY_PATH is not set in the .env file")

# Initialize Firebase with the service account JSON
cred = credentials.Certificate(firebase_key_path)
firebase_admin.initialize_app(cred)

db = firestore.client()

print("Firebase initialized successfully!")