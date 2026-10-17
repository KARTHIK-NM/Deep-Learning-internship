# Handwritten Digit Classifier

## Project Overview

This mini project uses a neural network to recognize handwritten digits from **0 to 9**. It uses the MNIST dataset, which contains grayscale images of handwritten digits.

The project is beginner-friendly and demonstrates how to train and evaluate a simple deep learning model.

## Objectives

- Recognize handwritten digits from 0 to 9.
- Train a fully connected neural network.
- Display sample predictions.
- Measure test accuracy, precision, and recall.
- Display a confusion matrix.
- Show five incorrect predictions and briefly analyze possible reasons.
- Plot training and validation accuracy and loss.

## Technologies Used

- Python
- TensorFlow / Keras
- NumPy
- Matplotlib
- Scikit-learn

## Requirements

Install the required libraries:

```bash
pip install tensorflow matplotlib scikit-learn numpy
```

## How to Run

1. Install Python.
2. Install the libraries listed above.
3. Save the Python code in a file named `handwritten_digit_classifier.py`, or copy it into a Jupyter Notebook.
4. Run the file or notebook.
5. The first run may download the MNIST dataset automatically, so an internet connection may be required.

## How the Project Works

1. **Load the data:** Load the MNIST training and testing images.
2. **View a sample:** Display one handwritten digit.
3. **Normalize images:** Divide pixel values by 255 so they fall between 0 and 1.
4. **Build the neural network:** Flatten each 28 × 28 image, pass it through a hidden layer with 128 neurons using ReLU, and use a 10-neuron Softmax output layer.
5. **Train the model:** Train for five epochs and use 10% of the training data for validation.
6. **Evaluate the model:** Calculate test loss, accuracy, precision, and recall.
7. **Show predictions:** Display actual and predicted digits.
8. **Analyze errors:** Find and display five incorrect predictions.
9. **Plot graphs:** Show training/validation accuracy and loss.
10. **View the confusion matrix:** Compare actual digit labels with predicted labels.

## Model Architecture

| Layer | Purpose |
|---|---|
| `Flatten(input_shape=(28, 28))` | Converts each image into a one-dimensional list of pixels |
| `Dense(128, activation="relu")` | Learns patterns in the images |
| `Dense(10, activation="softmax")` | Produces scores for digits 0–9 |

The model uses the **Adam** optimizer and **sparse categorical cross-entropy** loss.

## Expected Output

When the program finishes, it displays:

- A sample MNIST image.
- Training progress.
- Test accuracy and test loss.
- Ten sample predictions.
- Accuracy, precision, and recall.
- A confusion matrix.
- Five incorrect predictions.
- Training and validation accuracy graphs.
- Training and validation loss graphs.

Actual results are generated when the model runs and may vary slightly by environment.

## Error Analysis

Some predictions may be incorrect because:

- Two digits can have similar shapes.
- A digit may be unclear or poorly written.
- People write the same digit in different ways.
- The model may not have learned every useful pattern.

More training, suitable model changes, or further tuning may improve performance.

## Conclusion

This project demonstrates a simple deep learning workflow for handwritten digit classification. It trains a neural network on MNIST and evaluates its performance using classification metrics, a confusion matrix, sample predictions, and graphs.

## Dataset

**MNIST handwritten digit dataset**, available through TensorFlow/Keras:

```python
tf.keras.datasets.mnist.load_data()
```
