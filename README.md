# NeuroDigit: Real-Time AI Handwritten Digit Recognizer

A full-stack deep learning web application that recognizes handwritten digits in real time. Powered by a custom **PyTorch Convolutional Neural Network (CNN)** trained on the MNIST dataset (**99.54% test accuracy**) and served via a **FastAPI** backend with a modern dark-mode interactive canvas interface.

---

## Features

- **Real-Time Interactive Canvas**: Draw digits with smooth anti-aliased strokes, adjustable brush width (12–32px), eraser tool, undo stack, and clear controls.
- **Instant Neural Inference**: Sub-5ms PyTorch model inference that updates continuously as you draw.
- **NIST Center-of-Mass Preprocessing**: Automatically extracts bounding boxes, preserves aspect ratio into $20\times 20$, and centers the digit via Center-of-Mass into a $28\times 28$ tensor (matching official NIST/MNIST data preparation).
- **"Model's Eye" Live Tensor View**: Displays the exact $28\times 28$ normalized grayscale tensor being processed by the model in real time.
- **Probability Distribution**: Real-time softmax probability bars across all 10 digits ($0$–$9$), highlighting top-1/top-2 candidates and calculating Shannon entropy.
- **MNIST Benchmark Presets**: 10 one-click preset buttons to load authentic test samples from the MNIST dataset directly onto the canvas.
- **Architecture & Metrics Modal**: In-app inspection drawer showing the complete layer pipeline and epoch-by-epoch training convergence.

---

## Model Architecture

The custom `DigitCNN` architecture is optimized for high accuracy and fast CPU/GPU inference:

```
Input: [Batch, 1, 28, 28] (Grayscale, normalized 0.0 to 1.0)
│
├── Conv Block 1:
│   ├── Conv2D(1 -> 32, kernel=3, padding=1) + BatchNorm2d + ReLU
│   ├── Conv2D(32 -> 32, kernel=3, padding=1) + BatchNorm2d + ReLU
│   ├── MaxPool2d(2, 2)  --> [Batch, 32, 14, 14]
│   └── Dropout2d(0.25)
│
├── Conv Block 2:
│   ├── Conv2D(32 -> 64, kernel=3, padding=1) + BatchNorm2d + ReLU
│   ├── Conv2D(64 -> 64, kernel=3, padding=1) + BatchNorm2d + ReLU
│   ├── MaxPool2d(2, 2)  --> [Batch, 64, 7, 7]
│   └── Dropout2d(0.25)
│
└── Dense Classifier:
    ├── Flatten()        --> [Batch, 3136]
    ├── Linear(3136 -> 256) + BatchNorm1d + ReLU
    ├── Dropout(0.4)
    └── Linear(256 -> 10) --> [Batch, 10] (Logits / Softmax)
```

---

## Training Results

Trained on 60,000 MNIST training images and evaluated on 10,000 unseen test images using the **AdamW** optimizer with **Cosine Annealing** learning rate decay:

| Epoch | Train Loss | Train Accuracy | Validation Loss | Test Accuracy |
| :---: | :---: | :---: | :---: | :---: |
| 1 | 0.1529 | 95.96% | 0.0331 | 98.86% |
| 2 | 0.0529 | 98.43% | 0.0230 | 99.26% |
| 3 | 0.0353 | 98.91% | 0.0207 | 99.31% |
| 4 | 0.0254 | 99.22% | 0.0155 | 99.40% |
| **5** | **0.0211** | **99.37%** | **0.0142** | **99.54%** |

- **Final Test Accuracy**: **`99.54%`**
- **Inference Latency**: $\approx 2\text{--}4\text{ ms}$ on CPU

---

## Project Structure

```
project/
├── app.py                 # FastAPI backend, preprocessing pipeline, and inference API
├── train.py               # PyTorch CNN training script on MNIST dataset
├── model/
│   ├── digit_cnn.pth      # Saved PyTorch model weights (99.54% test accuracy)
│   └── metadata.json      # Training history, metrics, and MNIST sample images
├── static/
│   ├── index.html         # Web application layout and components
│   ├── style.css          # Dark-mode design system with glassmorphism
│   └── app.js             # Canvas drawing logic, debounce engine, and API integration
└── README.md              # Project documentation
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.10+
- `pip`

### 2. Install Dependencies
```bash
pip install torch torchvision fastapi uvicorn pillow scipy numpy
```

*(Optional: `tensorflow` or `torchvision` for downloading the MNIST dataset if training from scratch)*

---

## Usage

### Run the Web Application
Start the Uvicorn server:
```bash
python -m uvicorn app:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to:
```
http://127.0.0.1:8000
```

### (Optional) Retrain the Model
To retrain the neural network and update the model weights:
```bash
python train.py
```
This will train the CNN for 5 epochs on the MNIST dataset and save the new weights to `model/digit_cnn.pth` and stats to `model/metadata.json`.

---

## API Reference

### `POST /api/predict`
Predicts the handwritten digit from canvas image data.

- **Request Body**:
  ```json
  {
    "image": "data:image/png;base64,..."
  }
  ```
- **Response**:
  ```json
  {
    "prediction": 3,
    "confidence": 0.9984,
    "probabilities": [0.0, 0.0, 0.0, 0.9984, 0.0, 0.0012, ...],
    "processed_tensor": [[... 28x28 matrix ...]],
    "entropy": 0.0124,
    "inference_time_ms": 2.45
  }
  ```

### `GET /api/info`
Returns model metadata, architecture description, training convergence history, and benchmark test samples.

---

## Keyboard Shortcuts

| Shortcut | Action |
| :---: | :--- |
| <kbd>B</kbd> | Switch to Brush (Draw) mode |
| <kbd>E</kbd> | Switch to Eraser mode |
| <kbd>C</kbd> | Clear the canvas |
| <kbd>Ctrl</kbd> + <kbd>Z</kbd> | Undo last brush stroke |
