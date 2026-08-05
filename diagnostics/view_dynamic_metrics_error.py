import sys
import torch
import joblib
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.metrics import classification_report, confusion_matrix

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from train_Transformer import ASLTransformerClassifier, FEATURE_DIM, SEQUENCE_LENGTH

DATA_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Augmented" / "val"
MODELS_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODELS_DIR / "asl_dynamic_transformer.pth"
LABEL_ENCODER_PATH = MODELS_DIR / "dynamic_label_encoder.pkl"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def main():
    if not MODEL_PATH.exists() or not LABEL_ENCODER_PATH.exists():
        print("Missing model artifacts in models/")
        return

    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    classes = list(label_encoder.classes_)

    # Load validation data
    val_sequences, val_labels = [], []
    for class_folder in [f for f in DATA_DIR.iterdir() if f.is_dir()]:
        label = class_folder.name
        for npy_file in class_folder.glob("*.npy"):
            seq = np.load(npy_file)
            if seq.shape == (SEQUENCE_LENGTH, FEATURE_DIM):
                val_sequences.append(seq)
                val_labels.append(label)

    X_val = np.array(val_sequences)
    y_val = label_encoder.transform(val_labels)

    # Load model
    model = ASLTransformerClassifier(
        input_dim=FEATURE_DIM, d_model=128, nhead=4, num_layers=3, num_classes=len(classes), dropout=0.2
    ).to(DEVICE)
    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.eval()

    # Inference
    inputs = torch.tensor(X_val, dtype=torch.float32).to(DEVICE)
    with torch.no_grad():
        logits = model(inputs)
        preds = torch.argmax(logits, dim=1).cpu().numpy()

    # Calculate confusion matrix and zero out correct predictions
    cm = confusion_matrix(y_val, preds)
    error_matrix = cm.copy()
    np.fill_diagonal(error_matrix, 0)

    # Plot Error Matrix Heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(error_matrix, annot=True, fmt='d', cmap='Reds', xticklabels=classes, yticklabels=classes)
    plt.title("ASL Dynamic Transformer Error Isolation Matrix", fontsize=14)
    plt.xlabel("Predicted Sign")
    plt.ylabel("Actual Sign")
    plt.tight_layout()

    out_fig = PROJECT_ROOT / "diagnostics" / "dynamic_error_matrix.png"
    plt.savefig(out_fig)
    print(f"✓ Saved Dynamic Error Matrix plot to '{out_fig.resolve()}'")
    plt.show()


if __name__ == "__main__":
    main()