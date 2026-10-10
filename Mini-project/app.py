import base64
import io
import json
import os
import time
import numpy as np
from PIL import Image
import torch
import torch.nn as nn
from scipy import ndimage
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# CNN Architecture matching training
class DigitCNN(nn.Module):
    def __init__(self):
        super(DigitCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(64 * 7 * 7, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.4),
            nn.Linear(256, 10)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

app = FastAPI(title="NeuroDigit API", version="1.0.0")

# Mount static folder
app.mount("/static", StaticFiles(directory="static"), name="static")

# Device & Model
device = torch.device("cpu")
model = DigitCNN().to(device)
model_path = os.path.join("model", "digit_cnn.pth")
metadata_path = os.path.join("model", "metadata.json")

def load_trained_weights():
    if os.path.exists(model_path):
        model.load_state_dict(torch.load(model_path, map_location=device))
        model.eval()
        print(f"Loaded weights from {model_path}")
        return True
    return False

# Attempt load
load_trained_weights()

class PredictRequest(BaseModel):
    image: str

def preprocess_image(base64_str: str):
    """
    Decodes canvas image, detects strokes, crops bounding box,
    resizes to fit 20x20, centers by center of mass into 28x28,
    and returns normalized tensor + 28x28 list.
    """
    if "," in base64_str:
        base64_str = base64_str.split(",", 1)[1]
    
    img_bytes = base64.b64decode(base64_str)
    img = Image.open(io.BytesIO(img_bytes)).convert("RGBA")
    
    # Process transparency/background:
    # Canvas draws white lines on black background.
    # If transparent pixels exist, composite onto black background
    bg = Image.new("RGBA", img.size, (0, 0, 0, 255))
    composite = Image.alpha_composite(bg, img)
    gray = composite.convert("L")
    arr = np.array(gray, dtype=np.float32)
    
    # Check if empty (stroke pixel threshold)
    threshold = 30
    mask = arr > threshold
    if not np.any(mask):
        return None, None
    
    # Find bounding box
    rows = np.any(mask, axis=1)
    cols = np.any(mask, axis=0)
    ymin, ymax = np.where(rows)[0][[0, -1]]
    xmin, xmax = np.where(cols)[0][[0, -1]]
    
    # Box dimensions
    h = ymax - ymin + 1
    w = xmax - xmin + 1
    
    if h < 4 or w < 4:
        return None, None
    
    # Crop bounding box with 1px padding
    ymin_pad = max(0, ymin - 1)
    ymax_pad = min(arr.shape[0] - 1, ymax + 1)
    xmin_pad = max(0, xmin - 1)
    xmax_pad = min(arr.shape[1] - 1, xmax + 1)
    crop = arr[ymin_pad:ymax_pad+1, xmin_pad:xmax_pad+1]
    
    # Resize preserving aspect ratio into 20x20
    crop_img = Image.fromarray(crop.astype(np.uint8))
    crop_h, crop_w = crop.shape
    if crop_h > crop_w:
        factor = 20.0 / crop_h
        new_h = 20
        new_w = max(1, int(round(crop_w * factor)))
    else:
        factor = 20.0 / crop_w
        new_w = 20
        new_h = max(1, int(round(crop_h * factor)))
        
    resized = crop_img.resize((new_w, new_h), Image.Resampling.BILINEAR)
    resized_arr = np.array(resized, dtype=np.float32)
    
    # Place inside 28x28 image initially at center
    padded = np.zeros((28, 28), dtype=np.float32)
    y_off = (28 - new_h) // 2
    x_off = (28 - new_w) // 2
    padded[y_off:y_off+new_h, x_off:x_off+new_w] = resized_arr
    
    # Center of mass alignment (Standard MNIST normalization)
    cy, cx = ndimage.center_of_mass(padded)
    if not np.isnan(cy) and not np.isnan(cx):
        shift_y = np.clip(np.round(13.5 - cy), -4, 4)
        shift_x = np.clip(np.round(13.5 - cx), -4, 4)
        padded = ndimage.shift(padded, (shift_y, shift_x), mode='constant', cval=0.0)
    
    # Clamp and normalize 0..1
    padded = np.clip(padded, 0.0, 255.0) / 255.0
    tensor = torch.from_numpy(padded).unsqueeze(0).unsqueeze(0).float()
    
    return tensor, padded.tolist()

@app.get("/")
def read_root():
    return FileResponse("static/index.html")

@app.post("/api/predict")
def predict(req: PredictRequest):
    if not os.path.exists(model_path):
        # Check if model exists now
        if not load_trained_weights():
            raise HTTPException(status_code=503, detail="Model is currently training. Please wait a moment.")
    else:
        model.eval()

    tensor, processed_28x28 = preprocess_image(req.image)
    if tensor is None:
        return {
            "prediction": None,
            "confidence": 0.0,
            "probabilities": [0.0] * 10,
            "processed_tensor": None,
            "inference_time_ms": 0.0
        }
    
    start_time = time.perf_counter()
    with torch.no_grad():
        logits = model(tensor.to(device))
        probs = torch.softmax(logits, dim=1).squeeze(0).cpu().numpy()
        
    latency_ms = (time.perf_counter() - start_time) * 1000.0
    pred = int(np.argmax(probs))
    conf = float(probs[pred])
    probs_list = [round(float(p), 4) for p in probs]
    
    # Compute Shannon Entropy
    p_safe = np.clip(probs, 1e-12, 1.0)
    entropy = float(-np.sum(p_safe * np.log(p_safe)))

    return {
        "prediction": pred,
        "confidence": conf,
        "probabilities": probs_list,
        "processed_tensor": processed_28x28,
        "entropy": round(entropy, 4),
        "inference_time_ms": round(latency_ms, 2)
    }

@app.get("/api/info")
def get_info():
    if os.path.exists(metadata_path):
        with open(metadata_path, "r") as f:
            data = json.load(f)
        return data
    return {
        "architecture": "DigitCNN",
        "train_samples": 60000,
        "test_samples": 10000,
        "final_val_accuracy": "Training in progress..."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=False)
