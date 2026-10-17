"""
Plant Disease Classification Model Training Pipeline
Fine-tunes a pre-trained MobileNetV2 backbone on PlantVillage leaf images.
"""

import os
import json
import time
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers, callbacks

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_DIR = os.path.join(BASE_DIR, "dataset")
MODEL_DIR = os.path.join(BASE_DIR, "model")
STATIC_IMG_DIR = os.path.join(BASE_DIR, "static", "img")

IMG_SIZE = (224, 224)
BATCH_SIZE = 32
STAGE1_EPOCHS = 6
STAGE2_EPOCHS = 3

def main():
    os.makedirs(MODEL_DIR, exist_ok=True)
    os.makedirs(STATIC_IMG_DIR, exist_ok=True)

    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")

    print(f"Loading training data from: {train_dir}")
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=True,
        seed=42
    )

    print(f"Loading validation data from: {val_dir}")
    val_ds = tf.keras.utils.image_dataset_from_directory(
        val_dir,
        labels="inferred",
        label_mode="categorical",
        image_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        shuffle=False
    )

    class_names = train_ds.class_names
    num_classes = len(class_names)
    print(f"\nFound {num_classes} classes:")
    for idx, name in enumerate(class_names):
        print(f"  [{idx:02d}] {name}")

    # Save class names mapping
    with open(os.path.join(MODEL_DIR, "class_names.json"), "w") as f:
        json.dump(class_names, f, indent=2)

    # Performance optimization
    AUTOTUNE = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=AUTOTUNE)
    val_ds = val_ds.prefetch(buffer_size=AUTOTUNE)

    # Data augmentation pipeline
    data_augmentation = tf.keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.15),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
    ], name="data_augmentation")

    print("\nInitializing pre-trained MobileNetV2 backbone (ImageNet weights)...")
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(IMG_SIZE[0], IMG_SIZE[1], 3),
        include_top=False,
        weights="imagenet"
    )
    base_model.trainable = False

    # Model architecture
    inputs = tf.keras.Input(shape=(IMG_SIZE[0], IMG_SIZE[1], 3))
    x = data_augmentation(inputs)
    x = tf.keras.applications.mobilenet_v2.preprocess_input(x)
    x = base_model(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.BatchNormalization()(x)
    x = layers.Dense(128, activation="relu", kernel_regularizer=tf.keras.regularizers.l2(1e-4))(x)
    x = layers.Dropout(0.3)(x)
    outputs = layers.Dense(num_classes, activation="softmax")(x)

    model = tf.keras.Model(inputs, outputs, name="PlantDiseaseMobileNetV2")

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-3),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy")]
    )

    model.summary()

    start_time = time.time()

    # Stage 1: Feature Extraction (Backbone Frozen)
    print(f"\n--- Stage 1: Training Classification Head ({STAGE1_EPOCHS} epochs) ---")
    history_stage1 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_EPOCHS,
        verbose=1
    )

    # Stage 2: Fine-Tuning Top Layers of Backbone
    print(f"\n--- Stage 2: Fine-Tuning Top 30 Layers ({STAGE2_EPOCHS} epochs) ---")
    base_model.trainable = True
    fine_tune_at = len(base_model.layers) - 30
    for layer in base_model.layers[:fine_tune_at]:
        layer.trainable = False

    model.compile(
        optimizer=optimizers.Adam(learning_rate=1e-4),
        loss="categorical_crossentropy",
        metrics=["accuracy", tf.keras.metrics.TopKCategoricalAccuracy(k=3, name="top_3_accuracy")]
    )

    history_stage2 = model.fit(
        train_ds,
        validation_data=val_ds,
        epochs=STAGE1_EPOCHS + STAGE2_EPOCHS,
        initial_epoch=STAGE1_EPOCHS,
        verbose=1
    )

    elapsed_time = round(time.time() - start_time, 2)
    print(f"\nTraining completed in {elapsed_time}s.")

    # Evaluation
    print("\nEvaluating final model on validation dataset...")
    val_loss, val_acc, val_top3 = model.evaluate(val_ds, verbose=0)
    print(f"Validation Loss: {val_loss:.4f}")
    print(f"Validation Accuracy: {val_acc * 100:.2f}%")
    print(f"Validation Top-3 Accuracy: {val_top3 * 100:.2f}%")

    # Save model
    model_path = os.path.join(MODEL_DIR, "plant_disease_model.keras")
    model.save(model_path)
    print(f"Model saved to: {model_path}")

    # Combine histories
    acc = history_stage1.history["accuracy"] + history_stage2.history["accuracy"]
    val_acc_hist = history_stage1.history["val_accuracy"] + history_stage2.history["val_accuracy"]
    loss = history_stage1.history["loss"] + history_stage2.history["loss"]
    val_loss_hist = history_stage1.history["val_loss"] + history_stage2.history["val_loss"]

    # Save training metrics JSON
    metrics = {
        "final_accuracy": float(val_acc),
        "final_loss": float(val_loss),
        "final_top3_accuracy": float(val_top3),
        "total_epochs": STAGE1_EPOCHS + STAGE2_EPOCHS,
        "classes_count": num_classes,
        "classes": class_names,
        "training_time_seconds": elapsed_time,
        "backbone": "MobileNetV2 (ImageNet pre-trained)",
        "input_resolution": "224x224x3",
        "parameters": model.count_params(),
        "history": {
            "accuracy": [float(x) for x in acc],
            "val_accuracy": [float(x) for x in val_acc_hist],
            "loss": [float(x) for x in loss],
            "val_loss": [float(x) for x in val_loss_hist]
        }
    }

    with open(os.path.join(MODEL_DIR, "training_metrics.json"), "w") as f:
        json.dump(metrics, f, indent=2)

    # Plot metrics
    plt.figure(figsize=(12, 5), dpi=150)
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")

    # Accuracy Plot
    plt.subplot(1, 2, 1)
    plt.plot(range(1, len(acc) + 1), acc, marker='o', color='#10b981', label='Training Accuracy', linewidth=2)
    plt.plot(range(1, len(val_acc_hist) + 1), val_acc_hist, marker='s', color='#3b82f6', label='Validation Accuracy', linewidth=2)
    plt.axvline(x=STAGE1_EPOCHS + 0.5, color='#ef4444', linestyle='--', label='Fine-Tuning Start')
    plt.title('Training & Validation Accuracy', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Epoch', fontsize=10)
    plt.ylabel('Accuracy', fontsize=10)
    plt.ylim([0.0, 1.05])
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)

    # Loss Plot
    plt.subplot(1, 2, 2)
    plt.plot(range(1, len(loss) + 1), loss, marker='o', color='#f59e0b', label='Training Loss', linewidth=2)
    plt.plot(range(1, len(val_loss_hist) + 1), val_loss_hist, marker='s', color='#8b5cf6', label='Validation Loss', linewidth=2)
    plt.axvline(x=STAGE1_EPOCHS + 0.5, color='#ef4444', linestyle='--', label='Fine-Tuning Start')
    plt.title('Training & Validation Loss', fontsize=12, fontweight='bold', pad=10)
    plt.xlabel('Epoch', fontsize=10)
    plt.ylabel('Loss', fontsize=10)
    plt.legend(loc='upper right')
    plt.grid(True, alpha=0.3)

    plt.tight_layout()
    chart_path = os.path.join(MODEL_DIR, "training_history.png")
    static_chart_path = os.path.join(STATIC_IMG_DIR, "training_history.png")
    plt.savefig(chart_path)
    plt.savefig(static_chart_path)
    plt.close()
    print(f"Training charts saved to {chart_path} and {static_chart_path}")

if __name__ == "__main__":
    main()
