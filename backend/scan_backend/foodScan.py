from fastapi import FastAPI, HTTPException
from firebase_admin import credentials, firestore, initialize_app
from dotenv import load_dotenv
import os
import requests

# Initialize FastAPI app
app = FastAPI()

# Load environment variables
load_dotenv(dotenv_path="shared/.env")
aicook_api_key = os.getenv("AICOOK_API_KEY")

# Firebase setup
firebase_key_path = os.getenv("FIREBASE_KEY_PATH")
if not firebase_key_path:
    raise ValueError("FIREBASE_KEY_PATH is not set in the .env file")

cred = credentials.Certificate(firebase_key_path)
initialize_app(cred)
db = firestore.client()

    
@app.get("/")
async def root():
    return {"message": "Welcome to the Food Scan API!"}

@app.get("/images/{document_id}")
async def get_image_url(document_id: str):
    try:
        # Reference the document by its ID in the "images" collection
        doc_ref = db.collection("images").document(document_id)
        doc = doc_ref.get()

        # Check if the document exists
        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found")

        # Extract the `imageURL` field from the document
        data = doc.to_dict()
        image_url = data.get("imageURL")
        if not image_url:
            raise HTTPException(status_code=404, detail=f"No 'imageURL' field found in document '{document_id}'")

        # Return the image URL
        return {"document_id": document_id, "image_url": image_url}
    except Exception as e:
        print(f"Error fetching document with ID {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch the document")



# Endpoint to retrieve all image URLs
@app.get("/images")
async def get_all_image_urls():
    try:
        docs = db.collection("images").stream()
        image_urls = []
        for doc in docs:
            data = doc.to_dict()
            image_url = data.get("imageUrl")
            if image_url:
                image_urls.append({"document_id": doc.id, "image_url": image_url})
        
        if not image_urls:
            raise HTTPException(status_code=404, detail="No images found in the database")
        
        return {"images": image_urls}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving images: {str(e)}")
    
@app.get("/process-image/{document_id}")
async def process_image(document_id: str):
    try:
        # Step 1: Fetch the image URL from Firestore
        doc_ref = db.collection("images").document(document_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found")

        data = doc.to_dict()
        image_url = data.get("imageURL")
        if not image_url:
            raise HTTPException(status_code=404, detail=f"No 'imageURL' field found in document '{document_id}'")

        # Step 2: Send the image URL to the AI Cook API
        ingredients = process_image_with_aicook(image_url)
        if ingredients is None:
            raise HTTPException(status_code=500, detail="Failed to process image with AI Cook API")

        # Step 3: Return the ingredients
        return {
            "document_id": document_id,
            "image_url": image_url,
            "ingredients": ingredients
        }
    except Exception as e:
        print(f"Error processing image for document ID {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the image")
    


def infer_image_with_aicook(image_url):
    try:
        aicook_api_url = "https://detect.roboflow.com/aicook-lcv4d/3"
        api_key = "fAwcjwOeWTzCAttEENEQ"

        # URL-encoded query parameters
        params = {
            "api_key": api_key,
            "image": image_url
        }

        response = requests.post(aicook_api_url, params=params)
        if response.status_code != 200:
            print(f"AI Cook API Error: {response.status_code}, {response.text}")
            return None

        # Extract the JSON data
        response_data = response.json()

        # Extract the "class" from each prediction
        predictions = response_data.get("predictions", [])
        classes = [prediction["class"] for prediction in predictions]

        print("Extracted Classes:", classes)
        return classes
    except Exception as e:
        print(f"Error inferring image with AI Cook: {str(e)}")
        return None

@app.get("/process-database-image/{document_id}")
async def process_database_image(document_id: str):
    try:
        # Step 1: Fetch the image URL from Firestore
        db = firestore.client()
        doc_ref = db.collection("images").document(document_id)
        doc = doc_ref.get()

        if not doc.exists:
            raise HTTPException(status_code=404, detail=f"Document with ID '{document_id}' not found")

        data = doc.to_dict()
        image_url = data.get("imageURL")
        if not image_url:
            raise HTTPException(status_code=404, detail=f"No 'imageURL' field found in document '{document_id}'")

        # Step 2: Send the image URL to AI Cook and extract the "class" (ingredients)
        classes = infer_image_with_aicook(image_url)
        if classes is None:
            raise HTTPException(status_code=500, detail="Failed to process image with AI Cook API")

        # Step 3: Save extracted classes to the "ingredients" collection
        ingredients_collection = db.collection("ingredients")
        for ingredient in classes:
            ingredients_collection.add({"name": ingredient})

        # Step 4: Optionally update the original document with the classes
        doc_ref.update({"ingredients": classes})

        # Step 5: Return the extracted classes
        return {"document_id": document_id, "ingredients": classes}
    except Exception as e:
        print(f"Error processing image for document ID {document_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process the image")
