import joblib
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import LabelEncoder
from sklearn.utils.class_weight import compute_class_weight
from pathlib import Path
import math

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Augmented"
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_SAVE_PATH = MODELS_DIR / "asl_dynamic_transformer.pth"
LABEL_ENCODER_PATH = MODELS_DIR / "dynamic_label_encoder.pkl"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"⚡ Using Device: {DEVICE}")

BATCH_SIZE = 16
NUM_EPOCHS = 50
LEARNING_RATE = 0.0005
SEQUENCE_LENGTH = 30
FEATURE_DIM = 66  # Changed from 63 to 66


class DynamicASLDataset(Dataset):
    def __init__(self, sequences, labels):
        self.sequences = torch.tensor(sequences, dtype=torch.float32)
        self.labels = torch.tensor(labels, dtype=torch.long)

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return self.sequences[idx], self.labels[idx]


# Positional Encoding for Temporal Sequence Awareness
class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=50):
        super(PositionalEncoding, self).__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-math.log(10000.0) / d_model))
        
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.pe = pe.unsqueeze(0)  # Shape: (1, max_len, d_model)

    def forward(self, x):
        return x + self.pe[:, :x.size(1), :].to(x.device)


# Spatial-Temporal Transformer Classifier
class ASLTransformerClassifier(nn.Module):
    def __init__(self, input_dim, d_model=128, nhead=4, num_layers=3, num_classes=10, dropout=0.2):
        super(ASLTransformerClassifier, self).__init__()
        
        # Linear projection to Transformer dimension
        self.input_projection = nn.Linear(input_dim, d_model)
        self.pos_encoder = PositionalEncoding(d_model=d_model, max_len=SEQUENCE_LENGTH)
        
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=256,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=num_layers)
        
        self.fc1 = nn.Linear(d_model, 64)
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(dropout)
        self.fc2 = nn.Linear(64, num_classes)

    def forward(self, x):
        # x shape: (Batch, 30, FEATURE_DIM)
        x = self.input_projection(x)
        x = self.pos_encoder(x)
        
        out = self.transformer_encoder(x)  # (Batch, 30, d_model)
        
        # Mean Pooling over temporal tokens
        global_repr = torch.mean(out, dim=1)
        
        x = self.fc1(global_repr)
        x = self.relu(x)
        x = self.dropout(x)
        logits = self.fc2(x)
        return logits


def load_split_data(split_name):
    split_dir = DATA_DIR / split_name
    sequences, raw_labels = [], []

    for class_folder in [f for f in split_dir.iterdir() if f.is_dir()]:
        label = class_folder.name
        for npy_file in class_folder.glob("*.npy"):
            seq = np.load(npy_file)
            if seq.shape == (SEQUENCE_LENGTH, FEATURE_DIM):
                sequences.append(seq)
                raw_labels.append(label)

    return np.array(sequences), raw_labels


def main():
    X_train_raw, y_train_raw = load_split_data("train")
    X_val_raw, y_val_raw = load_split_data("val")

    label_encoder = LabelEncoder()
    all_labels = list(set(y_train_raw + y_val_raw))
    label_encoder.fit(all_labels)
    joblib.dump(label_encoder, LABEL_ENCODER_PATH)

    y_train = label_encoder.transform(y_train_raw)
    y_val = label_encoder.transform(y_val_raw)

    print(f"✓ Train Samples: {len(X_train_raw)} | Val Samples: {len(X_val_raw)}")
    print(f"✓ Total Classes: {len(label_encoder.classes_)}")

    train_loader = DataLoader(DynamicASLDataset(X_train_raw, y_train), batch_size=BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(DynamicASLDataset(X_val_raw, y_val), batch_size=BATCH_SIZE, shuffle=False)

    num_classes = len(label_encoder.classes_)
    model = ASLTransformerClassifier(
        input_dim=FEATURE_DIM, d_model=128, nhead=4, num_layers=3, num_classes=num_classes, dropout=0.2
    ).to(DEVICE)

    class_weights = compute_class_weight('balanced', classes=np.unique(y_train), y=y_train)
    criterion = nn.CrossEntropyLoss(weight=torch.tensor(class_weights, dtype=torch.float32).to(DEVICE))
    optimizer = torch.optim.AdamW(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-4)

    best_val_acc = 0.0
    print("\nTraining Spatial-Temporal Transformer Model...\n")

    for epoch in range(1, NUM_EPOCHS + 1):
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

        epoch_train_acc = (train_correct / len(X_train_raw)) * 100
        epoch_val_acc = (val_correct / len(X_val_raw)) * 100

        print(f"Epoch [{epoch:02d}/{NUM_EPOCHS}] | Train Acc: {epoch_train_acc:.2f}% | Val Acc: {epoch_val_acc:.2f}%")

        if epoch_val_acc > best_val_acc:
            best_val_acc = epoch_val_acc
            torch.save(model.state_dict(), MODEL_SAVE_PATH)

    print(f"\nTraining Complete! Peak Validation Accuracy: {best_val_acc:.2f}%")


if __name__ == "__main__":
    main()