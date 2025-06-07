from flask import Flask, request, jsonify
import tensorflow as tf
from keras.models import load_model # type: ignore
import numpy as np
from PIL import Image
import os
import json

from pymongo import MongoClient
import datetime

from flask_cors import CORS

app = Flask(__name__)

CORS(app)  # Enable CORS for the entire app

# Connect to MongoDB
client = MongoClient("mongodb+srv://admin123:EyeDisease123@cluster0.0dmadoo.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["eyeDiseaseDB"]  # Use your MongoDB database
collection = db["predictions"]  # Create/Use the predictions collection

# Load class labels from saved file
json_path = os.path.join(os.getcwd(), "ml_model", "class_labels.json")
with open(json_path, "r") as f:
    class_labels = json.load(f)


import os

model_path = os.path.join(os.getcwd(),"ml_model", "model.h5")
model = load_model(model_path)







print("Model input shape:", model.inputs)

@app.route('/')
def home():
    return "Flask ML API is running!"

@app.route('/login', methods=['POST'])
def login():
    data = request.json  # Get JSON data from frontend
    email = data.get("email")
    password = data.get("password")

    # Use the 'users' collection to verify user credentials
    users_collection = db["users"]  

    user = users_collection.find_one({"email": email})  # Find user by email

    if not user:
        return jsonify({"error": "User not found"}), 404

    # In production, compare hashed passwords securely!
    if user["password"] != password:
        return jsonify({"error": "Invalid password"}), 401

    return jsonify({"message": "Login successful", "user": {"name": user["name"], "email": user["email"]}}), 200

UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))  # Ensure it's in backend/uploads
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Create if it doesn't exist
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

@app.route('/predict', methods=['POST'])
def predict():
    if 'image' not in request.files:
        print("Debug: No image found in request")
        return jsonify({'error': 'No image provided'}), 400

    
    file = request.files['image']
    filename = file.filename

    try:
        # Fix: Use correctly defined config key `"UPLOAD_FOLDER"`
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)  
        
        # Save the image to "uploads" folder
        file.save(file_path)

        
        # print("Processing image:", file_path)
        # Preprocess the image
        img = Image.open(file_path).resize((150, 150))
        img_array = np.array(img).astype('float32') / 255.0
        img_array = img_array.reshape(1, 150, 150, 3)
        
        # print("Image shape before prediction:", img_array.shape)
        # Making the prediction
        prediction = model.predict(img_array)
        # print("Raw Model Output:", prediction)
        result = np.argmax(prediction, axis=1)
        predicted_label = class_labels.get(str(result[0]), "Unknown")
        # print("Final Predicted Disease:", predicted_label)

        # Store prediction in MongoDB
        collection.insert_one({
            'filename': filename,
            'file_path': file_path,
            'result': int(result[0]),
            'disease': predicted_label,
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

        # print("Predicted Class Index:", result[0])  # Ensure correct label extraction
        # print("Mapped Class Labels:", class_labels)  # Debug JSON mapping
        # print("Extracted Disease Name:", predicted_label)  # Confirm disease name
        print("Raw Model Output:", prediction)
        print("Argmax Result:", result[0])
        print("Disease Label Mapped:", predicted_label)
        print("Available Labels:", class_labels)


        return jsonify({
        "message": "Prediction successful!",
        "filePath": f"/uploads/{filename}",
        "result": int(result[0]),  # Send numeric class result
        "disease": predicted_label  # Include the disease name
        })


    except Exception as e:
        # print("Prediction Error:", e)
        return jsonify({'error': str(e)}), 500

    except Exception as e:
        # print("Prediction Error:", e)  # Debugging: Print error to Flask logs
        return jsonify({'error': str(e)}), 500  # Return error response in JSON format
    


from flask import send_from_directory

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename, as_attachment=False)


@app.route('/results', methods=['GET'])
def get_results():
    results = list(collection.find({}, {"_id": 0}))  # Exclude MongoDB ID
    return jsonify({'predictions': results})

@app.route('/register', methods=['POST'])
def register():
    data = request.json  # Get JSON data from frontend
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")

    # Use the 'users' collection for storing user data
    users_collection = db["users"]  # Specify the 'users' collection

    # Check if the user already exists
    if users_collection.find_one({"email": email}):  # Query the 'users' collection
        return jsonify({"error": "Email already registered"}), 409

    # Save the new user to the 'users' collection in MongoDB
    users_collection.insert_one({
        "name": name,
        "email": email,
        "password": password  # NOTE: Store passwords securely with hashing (e.g., bcrypt) in production
    })

    return jsonify({"message": "User registered successfully"}), 201

if __name__ == "__main__":
    PORT = int(os.getenv("PORT", 5000))  # Render assigns PORT dynamically
    app.run(host="0.0.0.0", port=PORT)
  # Start Flask API on port 5001
