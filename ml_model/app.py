from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
from keras.models import load_model  # type: ignore
import numpy as np
from PIL import Image
import os
import json
from pymongo import MongoClient
import datetime

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for security in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Connect to MongoDB
client = MongoClient("mongodb+srv://admin123:EyeDisease123@cluster0.0dmadoo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["eyeDiseaseDB"]
collection = db["predictions"]

# Load class labels
with open("ml_model/class_labels.json", "r") as f:
    class_labels = json.load(f)


# Load ML model
model = load_model("ml_model/model1.h5")


# Setup Upload Folder
UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.get("/")
async def home():
    return {"message": "FastAPI ML Server is Running!"}

@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    user = db["users"].find_one({"email": email})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user["password"] != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return {"message": "Login successful", "user": {"name": user["name"], "email": user["email"]}}

@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        file_path = os.path.join(UPLOAD_FOLDER, image.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await image.read())  # Save uploaded image

        img = Image.open(file_path).resize((150, 150))
        img_array = np.array(img).astype("float32") / 255.0
        img_array = img_array.reshape(1, 150, 150, 3)

        prediction = model.predict(img_array)
        result = np.argmax(prediction, axis=1)[0]
        predicted_label = class_labels.get(str(result), "Unknown")

        # Store prediction in MongoDB
        collection.insert_one({
            "filename": image.filename,
            "file_path": file_path,
            "result": int(result),
            "disease": predicted_label,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        return {
            "message": "Prediction successful!",
            "filePath": f"/uploads/{image.filename}",
            "result": int(result),
            "disease": predicted_label
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results")
async def get_results():
    results = list(collection.find({}, {"_id": 0}))
    return {"predictions": results}

@app.post("/register")
async def register(name: str = Form(...), email: str = Form(...), password: str = Form(...)):
    users_collection = db["users"]

    if users_collection.find_one({"email": email}):
        raise HTTPException(status_code=409, detail="Email already registered")

    users_collection.insert_one({"name": name, "email": email, "password": password})
    return {"message": "User registered successfully"}

from fastapi.responses import FileResponse

@app.get("/uploads/{filename}")
async def uploaded_file(filename: str):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5001, reload=True)
