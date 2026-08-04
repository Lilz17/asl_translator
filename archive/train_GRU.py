import os
import joblib
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight  # <-- Added Import
from pathlib import Path

# ==========================================
# Path & Hardware Configuration
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
# Points to balanced, augmented sequence dataset
DATA_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Augmented"
MODELS_DIR = PROJECT_ROOT / "models"

MODELS_DIR.mkdir(parents=True, exist_ok=True)
MODEL_SAVE_PATH = MODELS_DIR / "asl_dynamic_gru.pth"
LABEL_ENCODER_PATH = MODELS_DIR / "dynamic_label_encoder.pkl"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"⚡ Using Device: {DEVICE}")

# Hyperparameters
BATCH_SIZE = 16
NUM_EPOCHS = 40
LEARNING_RATE = 0.001
SEQUENCE_LENGTH = 30
FEATURE_DIM = 63


# ==========================================
# PyTorch Dataset Wrapper
# ==========================================
class DynamicASLDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


# ==========================================
# GRU Model Architecture
# ==========================================
class GRUClassifier(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, num_classes, dropout=0.3):
        super(GRUClassifier, self).__init__()
        self.gru = nn.GRU(
            input_size=input_dim,
            hidden_size=hidden_dim,
            num_layers=num_layers,
            batch_first=True,
            dropout=dropout if num_layers > 1 else 0.0
        )
        self.fc1 = nn.Linear(hidden_dim, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        out, _ = self.gru(x)
        last_frame_out = out[:, -1, :]
        x = self.fc1(last_frame_out)
        x = self.relu(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        return logits


# ==========================================
# Data Loading
# ==========================================
def load_data():
    sequences = []
    raw_labels = []

    class_folders = [f for f in DATA_DIR.iterdir() if f.is_dir()]
    if not class_folders:
        raise FileNotFoundError(f"No class folders found under {DATA_DIR}")

    for class_folder in class_folders:
        label = class_folder.name
        npy_files = list(class_folder.glob("*.npy"))
        
        for npy_file in npy_files:
            seq = np.load(npy_file)
            if seq.shape == (SEQUENCE_LENGTH, FEATURE_DIM):
                sequences.append(seq)
                raw_labels.append(label)

    sequences = np.array(sequences)
    
    label_encoder = LabelEncoder()
    encoded_labels = label_encoder.fit_transform(raw_labels)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)
    
    print(f"✓ Loaded {len(sequences)} sequence samples across {len(label_encoder.classes_)} classes.")
    print(f"✓ Label Encoder saved to '{LABEL_ENCODER_PATH}'\n")

    return sequences, encoded_labels, label_encoder


# ==========================================
# Main Training Loop
# ==========================================
def main():
    sequences, labels, label_encoder = load_data()
    num_classes = len(label_encoder.classes_)

    # Stratified Train/Val split
    X_train, X_val, y_train, y_val = train_test_split(
        sequences, labels, test_size=0.2, random_state=42, stratify=labels
    )

    train_dataset = DynamicASLDataset(X_train, y_train)
    val_dataset = DynamicASLDataset(X_val, y_val)

    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE, shuffle=False)

    # Initialize Model
    model = GRUClassifier(
        input_dim=FEATURE_DIM,
        hidden_dim=128,
        num_layers=2,
        num_classes=num_classes,
        dropout=0.3
    ).to(DEVICE)

    # ==========================================
    # Compute Class Weights & Loss Function
    # ==========================================
    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    class_weights_tensor = torch.tensor(class_weights, dtype=torch.float32).to(DEVICE)

    criterion = nn.CrossEntropyLoss(weight=class_weights_tensor)
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    best_val_acc = 0.0

    print("Starting Balanced GRU Training Loop...\n")

    for epoch in range(1, NUM_EPOCHS + 1):
        # Training Phase
        model.train()
        train_loss, train_correct = 0.0, 0
        for batch_x, batch_y in train_loader:
            batch_x, batch_y = batch_x.to(DEVICE), batch_y.to(DEVICE)

            optimizer.zero_grad()
            outputs = model(batch_x)
            loss = criterion(outputs, batch_y)
            loss.backward()
            optimizer.step()

            train_loss += loss.item() * batch_x.size(0)
            preds = torch.argmax(outputs, dim=1)
            train_correct += (preds == batch_y).sum().item()

        # Validation Phase
        model.eval()
        val_loss, val_correct = 0.0, 0
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x, batch_y = batch_x.to(DEVICE), batch_y.to(DEVICE)
                outputs = model(batch_x)
                loss = criterion(outputs, batch_y)

                val_loss += loss.item() * batch_x.size(0)
                preds = torch.argmax(outputs, dim=1)
                val_correct += (preds == batch_y).sum().item()

        # Epoch Metrics
        epoch_train_loss = train_loss / len(train_dataset)
        epoch_train_acc = (train_correct / len(train_dataset)) * 100
        epoch_val_loss = val_loss / len(val_dataset)
        epoch_val_acc = (val_correct / len(val_dataset)) * 100

        print(f"Epoch [{epoch:02d}/{NUM_EPOCHS}] "
              f"| Train Loss: {epoch_train_loss:.4f} - Acc: {epoch_train_acc:.2f}% "
              f"| Val Loss: {epoch_val_loss:.4f} - Acc: {epoch_val_acc:.2f}%")

        # Save Best Model Checkpoint
        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)

    print(f"\nTraining Complete! Peak Validation Accuracy: {best_val_acc:.2f}%")
    print(f"   Best model saved to: {MODEL_SAVE_PATH.resolve()}")


if __name__ == "__main__":
    main()