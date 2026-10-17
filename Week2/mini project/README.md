# PhytoScan AI — Plant Disease Detection & Agronomic Treatment Advisor

A deep learning foliar pathology web application built with **TensorFlow / Keras**, **MobileNetV2 (Transfer Learning & Fine-Tuning)**, and **Flask**. Allows agriculturalists, researchers, and home gardeners to upload or capture leaf photos, receive instant disease classifications with confidence scores, view probability distributions, and access organic/chemical remediation guides.

---

## Architecture Overview

```
                      +-----------------------------+
                      |     User Leaf Photo Input    |
                      |  (Upload / Camera / Sample) |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Preprocessing Pipeline   |
                      |  RGB Conversion & (224,224) |
                      |    MobileNetV2 Scaling      |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |   Fine-Tuned MobileNetV2    |
                      |  ImageNet Inverted Residuals|
                      |    GlobalAvgPool + Dense    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Softmax Probabilities    |
                      |  Top Prediction & Conf %    |
                      +--------------+--------------+
                                     |
                                     v
                      +-----------------------------+
                      |    Agronomic Knowledge Base |
                      | - Pathogen & Severity Level |
                      | - Symptoms & Visual Signs   |
                      | - Organic Remedies          |
                      | - Chemical Interventions    |
                      | - Cultural Prevention       |
                      +-----------------------------+
```

---

## Supported Crops & Pathologies (12 Classes)

| Crop | Condition | Pathogen Type | Typical Severity |
| :--- | :--- | :--- | :--- |
| **Apple** | Healthy Foliage | None | Optimal Health |
| **Apple** | Black Rot | Fungal (*Botryosphaeria obtusa*) | High |
| **Corn (Maize)** | Healthy Foliage | None | Optimal Health |
| **Corn (Maize)** | Common Rust | Fungal (*Puccinia sorghi*) | Moderate to High |
| **Bell Pepper** | Healthy Foliage | None | Optimal Health |
| **Bell Pepper** | Bacterial Spot | Bacterial (*Xanthomonas*) | High |
| **Potato** | Healthy Foliage | None | Optimal Health |
| **Potato** | Early Blight | Fungal (*Alternaria solani*) | Moderate to High |
| **Potato** | Late Blight | Oomycete (*Phytophthora infestans*) | Critical |
| **Tomato** | Healthy Foliage | None | Optimal Health |
| **Tomato** | Early Blight | Fungal (*Alternaria linariae*) | Moderate to High |
| **Tomato** | Late Blight | Oomycete (*Phytophthora infestans*) | Critical |

---

## Dataset Provenance & Collection

The images are collected from the open **PlantVillage Dataset** (Sharada P. Mohanty et al.):
* **Total Training Set**: 720 images (60 images &times; 12 classes)
* **Total Validation Set**: 180 images (15 images &times; 12 classes)
* **Quick-Test Field Samples**: 24 real leaf photos integrated into the UI
* Script: [`download_dataset.py`](file:///c:/deeplearning%20intern/week2/mini%20project/download_dataset.py) downloads directly with multi-threaded workers from GitHub.

---

## Model Training & Transfer Learning

* **Backbone**: MobileNetV2 pre-trained on ImageNet.
* **Stage 1 (Feature Extraction)**: Base backbone frozen, training custom classification head with Adam optimizer (`lr=1e-3`) for 6 epochs.
* **Stage 2 (Fine-Tuning)**: Top 30 depthwise-separable convolutional layers unfrozen, trained with Adam (`lr=1e-4`) for 3 epochs.
* **Validation Accuracy**: **86.67%**
* **Validation Top-3 Accuracy**: **97.22%**
* **Model Footprint**: ~9.2 MB (2.43M parameters) — optimized for fast CPU inference (<35ms).
* Training script: [`train_model.py`](file:///c:/deeplearning%20intern/week2/mini%20project/train_model.py)
* Model file: [`model/plant_disease_model.keras`](file:///c:/deeplearning%20intern/week2/mini%20project/model/plant_disease_model.keras)

---

## Project Structure

```
mini project/
├── dataset/                     # Train and validation image dataset
│   ├── train/                  # 12 class folders (60 images each)
│   └── val/                    # 12 class folders (15 images each)
├── model/
│   ├── plant_disease_model.keras # Fine-tuned Keras model weights
│   ├── class_names.json        # 12 class index mappings
│   ├── training_metrics.json   # Accuracy, loss, and history data
│   └── training_history.png    # Training & validation curves plot
├── static/
│   ├── css/
│   │   └── style.css           # Glassmorphic botanical theme
│   ├── js/
│   │   └── app.js              # Inference, drag-drop, camera & gauge controller
│   ├── img/
│   │   └── training_history.png# Plot displayed in Model Stats modal
│   ├── samples/                # 24 1-click test field leaf photos
│   └── uploads/                # Temporary uploaded images
├── templates/
│   └── index.html              # Responsive Flask web interface
├── app.py                      # Flask backend API & inference server
├── disease_info.py             # Rich botanical pathology database
├── download_dataset.py         # Concurrent PlantVillage downloader
├── train_model.py              # MobileNetV2 fine-tuning pipeline
└── requirements.txt            # Dependency manifest
```

---

## Quickstart

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web Application
```bash
python app.py
```
Open **[http://127.0.0.1:5000](http://127.0.0.1:5000)** in your browser.

---

## API Reference

### `POST /api/predict`
Diagnoses leaf pathology from uploaded file or sample preset.

* **Multipart form**: `file` (Image file)
* **Or JSON**: `{"sample_filename": "Apple_Black_rot_sample_1.JPG"}`
* **Response**:
```json
{
  "success": true,
  "prediction": {
    "crop": "Tomato (Solanum lycopersicum)",
    "condition": "Late Blight",
    "scientific_name": "Phytophthora infestans",
    "confidence": 98.4,
    "is_healthy": false,
    "pathogen_type": "Oomycete (Water Mold)",
    "severity": "Critical",
    "color_code": "#b91c1c",
    "description": "An aggressive, fast-moving pathogen...",
    "symptoms": [...],
    "organic_treatment": [...],
    "chemical_treatment": [...],
    "prevention": [...]
  },
  "top_predictions": [
    { "label": "Tomato — Late Blight", "confidence": 98.4, "color_code": "#b91c1c" },
    ...
  ],
  "image_url": "/static/uploads/..."
}
```

### `GET /api/samples`
Returns the gallery of 24 pre-loaded field leaf samples.

### `GET /api/model-info`
Returns model metadata, parameter count, validation metrics, and training history curves.
