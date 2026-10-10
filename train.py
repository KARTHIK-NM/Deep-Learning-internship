import os
import json
import time
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

# Define modern high-accuracy CNN architecture
class DigitCNN(nn.Module):
    def __init__(self):
        super(DigitCNN, self).__init__()
        self.features = nn.Sequential(
            # Block 1: 28x28 -> 14x14
            nn.Conv2d(1, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2, 2),
            nn.Dropout2d(0.25),
            
            # Block 2: 14x14 -> 7x7
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

def load_mnist_data():
    print("Loading MNIST dataset...")
    from tensorflow.keras.datasets import mnist
    (x_train, y_train), (x_test, y_test) = mnist.load_data()
    
    # Normalize to [0.0, 1.0] and add channel dimension (N, 1, 28, 28)
    x_train = x_train.astype(np.float32) / 255.0
    x_test = x_test.astype(np.float32) / 255.0
    
    x_train = np.expand_dims(x_train, axis=1)
    x_test = np.expand_dims(x_test, axis=1)
    
    tensor_x_train = torch.from_numpy(x_train)
    tensor_y_train = torch.from_numpy(y_train).long()
    tensor_x_test = torch.from_numpy(x_test)
    tensor_y_test = torch.from_numpy(y_test).long()
    
    train_dataset = TensorDataset(tensor_x_train, tensor_y_train)
    test_dataset = TensorDataset(tensor_x_test, tensor_y_test)
    
    return train_dataset, test_dataset, (x_test, y_test)

def train_model():
    train_dataset, test_dataset, (raw_test_x, raw_test_y) = load_mnist_data()
    
    batch_size = 128
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=256, shuffle=False)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Training on device: {device}")
    
    model = DigitCNN().to(device)
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    scheduler = optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=5)
    
    epochs = 5
    history = {"epochs": [], "train_loss": [], "train_acc": [], "val_loss": [], "val_acc": []}
    
    start_time = time.time()
    
    for epoch in range(1, epochs + 1):
        model.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for batch_idx, (data, target) in enumerate(train_loader):
            data, target = data.to(device), target.to(device)
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()
            
            running_loss += loss.item() * data.size(0)
            pred = output.argmax(dim=1, keepdim=True)
            correct += pred.eq(target.view_as(pred)).sum().item()
            total += data.size(0)
            
        scheduler.step()
        
        train_loss = running_loss / total
        train_acc = correct / total
        
        # Validation
        model.eval()
        val_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for data, target in test_loader:
                data, target = data.to(device), target.to(device)
                output = model(data)
                loss = criterion(output, target)
                val_loss += loss.item() * data.size(0)
                pred = output.argmax(dim=1, keepdim=True)
                val_correct += pred.eq(target.view_as(pred)).sum().item()
                val_total += data.size(0)
                
        val_loss = val_loss / val_total
        val_acc = val_correct / val_total
        
        history["epochs"].append(epoch)
        history["train_loss"].append(round(train_loss, 4))
        history["train_acc"].append(round(train_acc * 100, 2))
        history["val_loss"].append(round(val_loss, 4))
        history["val_acc"].append(round(val_acc * 100, 2))
        
        print(f"Epoch {epoch}/{epochs} | Train Loss: {train_loss:.4f} | Train Acc: {train_acc*100:.2f}% | Val Loss: {val_loss:.4f} | Val Acc: {val_acc*100:.2f}%")
        
    total_time = round(time.time() - start_time, 2)
    print(f"Training completed in {total_time}s with final test accuracy: {val_acc*100:.2f}%")
    
    # Save model weights
    os.makedirs("model", exist_ok=True)
    model_path = os.path.join("model", "digit_cnn.pth")
    torch.save(model.state_dict(), model_path)
    print(f"Model saved to {model_path}")
    
    # Save a few sample digits from test set for quick testing in frontend
    sample_digits = []
    # pick one sample for each digit 0-9
    found_digits = {}
    for i in range(len(raw_test_y)):
        digit = int(raw_test_y[i])
        if digit not in found_digits:
            img = (raw_test_x[i, 0] * 255).astype(np.uint8).tolist()
            found_digits[digit] = img
            if len(found_digits) == 10:
                break
    
    metadata = {
        "architecture": "DigitCNN (2x Conv Blocks + BatchNorm + Dropout + Dense 256)",
        "train_samples": 60000,
        "test_samples": 10000,
        "epochs": epochs,
        "training_time_seconds": total_time,
        "final_val_accuracy": round(val_acc * 100, 2),
        "history": history,
        "sample_digits": found_digits
    }
    
    with open(os.path.join("model", "metadata.json"), "w") as f:
        json.dump(metadata, f, indent=2)
    print("Metadata and sample digits saved.")

if __name__ == "__main__":
    train_model()
