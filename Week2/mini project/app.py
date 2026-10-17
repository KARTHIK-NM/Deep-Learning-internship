"""
Plant Disease Detection Flask Application
Serves deep learning inference, disease recommendations, and rich diagnostics UI.
"""

import os
import io
import json
import base64
import numpy as np
from PIL import Image
from flask import Flask, render_template, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import tensorflow as tf

from disease_info import get_disease_details, DISEASE_DATABASE

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "model")
MODEL_PATH = os.path.join(MODEL_DIR, "plant_disease_model.keras")
CLASS_NAMES_PATH = os.path.join(MODEL_DIR, "class_names.json")
METRICS_PATH = os.path.join(MODEL_DIR, "training_metrics.json")
SAMPLES_DIR = os.path.join(BASE_DIR, "static", "samples")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp"}

os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max upload
app.config["UPLOAD_FOLDER"] = UPLOAD_DIR

# Global model cache
model = None
class_names = []
training_metrics = {}

def load_ai_model():
    """Load trained Keras model and class names."""
    global model, class_names, training_metrics
    if os.path.exists(CLASS_NAMES_PATH):
        with open(CLASS_NAMES_PATH, "r") as f:
            class_names = json.load(f)
        print(f"Loaded {len(class_names)} classes from {CLASS_NAMES_PATH}")

    if os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            training_metrics = json.load(f)

    if os.path.exists(MODEL_PATH):
        try:
            print(f"Loading trained neural network from {MODEL_PATH}...")
            model = tf.keras.models.load_model(MODEL_PATH)
            print("Model loaded successfully into memory.")
        except Exception as e:
            print(f"Error loading model: {e}")
    else:
        print(f"Model file not found at {MODEL_PATH}. Waiting for training completion.")

# Attempt initial load
load_ai_model()

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_leaf_image(image: Image.Image):
    """Ensure image is in RGB format and resized to (224, 224)."""
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize((224, 224), Image.Resampling.BILINEAR)
    img_array = np.array(image, dtype=np.float32)
    img_batch = np.expand_dims(img_array, axis=0)
    return img_batch

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/samples", methods=["GET"])
def get_sample_gallery():
    """Return available sample leaf images for quick 1-click testing."""
    samples_manifest_path = os.path.join(SAMPLES_DIR, "samples.json")
    if os.path.exists(samples_manifest_path):
        with open(samples_manifest_path, "r") as f:
            samples = json.load(f)
        return jsonify({"success": True, "samples": samples})
    
    # Fallback scan
    samples = []
    if os.path.exists(SAMPLES_DIR):
        for f in os.listdir(SAMPLES_DIR):
            if allowed_file(f):
                samples.append({
                    "filename": f,
                    "label": f.replace("_", " ").rsplit(".", 1)[0].title(),
                    "class_id": "unknown"
                })
    return jsonify({"success": True, "samples": samples})

@app.route("/api/model-info", methods=["GET"])
def get_model_info():
    """Return model architecture and training validation metrics."""
    global model, class_names, training_metrics
    if not training_metrics and os.path.exists(METRICS_PATH):
        with open(METRICS_PATH, "r") as f:
            training_metrics = json.load(f)

    return jsonify({
        "success": True,
        "is_loaded": model is not None,
        "classes_count": len(class_names),
        "classes": class_names,
        "metrics": training_metrics
    })

@app.route("/api/disease-info/<class_id>", methods=["GET"])
def get_disease_info(class_id):
    """Return comprehensive treatment and care guide for a disease class."""
    details = get_disease_details(class_id)
    return jsonify({"success": True, "details": details})

@app.route("/api/predict", methods=["POST"])
def predict():
    """Predict plant disease from uploaded leaf image or sample preset."""
    global model, class_names
    if model is None:
        load_ai_model()
        if model is None:
            return jsonify({
                "success": False,
                "error": "The model is still training or could not be loaded. Please try again in a moment."
            }), 503

    image = None
    display_image_url = ""

    # Option 1: File upload
    if "file" in request.files:
        file = request.files["file"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_path)
            display_image_url = f"/static/uploads/{filename}"
            image = Image.open(save_path)

    # Option 2: Sample filename
    elif request.is_json and "sample_filename" in request.json:
        sample_filename = secure_filename(request.json["sample_filename"])
        sample_path = os.path.join(SAMPLES_DIR, sample_filename)
        if os.path.exists(sample_path):
            display_image_url = f"/static/samples/{sample_filename}"
            image = Image.open(sample_path)

    # Option 3: Base64 data (webcam or clipboard)
    elif request.is_json and "image_data" in request.json:
        try:
            data = request.json["image_data"]
            if "," in data:
                data = data.split(",")[1]
            img_bytes = base64.b64decode(data)
            image = Image.open(io.BytesIO(img_bytes))
            
            # Save uploaded snapshot
            import uuid
            snap_name = f"snapshot_{uuid.uuid4().hex[:8]}.jpg"
            snap_path = os.path.join(app.config["UPLOAD_FOLDER"], snap_name)
            image.convert("RGB").save(snap_path, "JPEG")
            display_image_url = f"/static/uploads/{snap_name}"
        except Exception as e:
            return jsonify({"success": False, "error": f"Invalid base64 image: {str(e)}"}), 400

    if image is None:
        return jsonify({"success": False, "error": "No valid image provided for analysis."}), 400

    try:
        # Preprocess and infer
        img_batch = preprocess_leaf_image(image)
        probabilities = model.predict(img_batch, verbose=0)[0]

        top_indices = np.argsort(probabilities)[::-1]
        top_idx = int(top_indices[0])
        top_class = class_names[top_idx]
        top_confidence = float(probabilities[top_idx])

        # Top 5 distribution
        predictions = []
        for idx in top_indices[:5]:
            cls_name = class_names[int(idx)]
            conf = float(probabilities[int(idx)])
            details = get_disease_details(cls_name)
            predictions.append({
                "class_id": cls_name,
                "label": f"{details['crop'].split(' (')[0]} — {details['condition']}",
                "confidence": round(conf * 100, 2),
                "is_healthy": details["is_healthy"],
                "color_code": details["color_code"]
            })

        disease_info = get_disease_details(top_class)

        return jsonify({
            "success": True,
            "prediction": {
                "class_id": top_class,
                "crop": disease_info["crop"],
                "condition": disease_info["condition"],
                "scientific_name": disease_info["scientific_name"],
                "confidence": round(top_confidence * 100, 2),
                "is_healthy": disease_info["is_healthy"],
                "pathogen_type": disease_info["pathogen_type"],
                "severity": disease_info["severity"],
                "color_code": disease_info["color_code"],
                "description": disease_info["description"],
                "symptoms": disease_info["symptoms"],
                "organic_treatment": disease_info["organic_treatment"],
                "chemical_treatment": disease_info["chemical_treatment"],
                "prevention": disease_info["prevention"]
            },
            "top_predictions": predictions,
            "image_url": display_image_url
        })
    except Exception as e:
        return jsonify({"success": False, "error": f"Inference failed: {str(e)}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
