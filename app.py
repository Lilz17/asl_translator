import sys
import torch
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Ensure src is in Python path
PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.append(str(PROJECT_ROOT / "src"))

from train_Transformer import ASLTransformerClassifier, FEATURE_DIM, SEQUENCE_LENGTH

app = FastAPI(title="ASL Translator API")

# Enable CORS so that the frontend can make requests without browser blocks
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Variables for Models
STATIC_MODEL = None
STATIC_ENCODER = None
DYNAMIC_MODEL = None
DYNAMIC_ENCODER = None
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


# Request Schemas
class StaticFrameInput(BaseModel):
    # Expecting 63 landmark values [x0, y0, z0, ..., x20, y20, z20]
    landmarks: List[float]


class DynamicSequenceInput(BaseModel):
    # Expecting sequence of shape (30, 66) as a flat or 2D list
    sequence: List[List[float]]


@app.on_event("startup")
def load_models():
    global STATIC_MODEL, STATIC_ENCODER, DYNAMIC_MODEL, DYNAMIC_ENCODER

    models_dir = PROJECT_ROOT / "models"
    
    # Load Static Artifacts
    static_model_path = models_dir / "asl_static_model.pkl"
    static_encoder_path = models_dir / "static_label_encoder.pkl"
    
    if static_model_path.exists():
        STATIC_MODEL = joblib.load(static_model_path)
        if static_encoder_path.exists():
            STATIC_ENCODER = joblib.load(static_encoder_path)
        print("✓ Static Model Loaded Successfully")

    # Load Dynamic Artifacts
    dynamic_model_path = models_dir / "asl_dynamic_transformer.pth"
    dynamic_encoder_path = models_dir / "dynamic_label_encoder.pkl"

    if dynamic_model_path.exists() and dynamic_encoder_path.exists():
        DYNAMIC_ENCODER = joblib.load(dynamic_encoder_path)
        num_classes = len(DYNAMIC_ENCODER.classes_)
        
        DYNAMIC_MODEL = ASLTransformerClassifier(
            input_dim=FEATURE_DIM, d_model=128, nhead=4, num_layers=3, num_classes=num_classes, dropout=0.2
        ).to(DEVICE)
        DYNAMIC_MODEL.load_state_dict(torch.load(dynamic_model_path, map_location=DEVICE, weights_only=True))
        DYNAMIC_MODEL.eval()
        print("✓ Dynamic Transformer Model Loaded Successfully")


@app.get("/")
def health_check():
    return {"status": "online", "device": str(DEVICE)}


@app.post("/predict/static")
def predict_static(data: StaticFrameInput):
    if STATIC_MODEL is None:
        raise HTTPException(status_code=500, detail="Static model not loaded.")
    
    if len(data.landmarks) != 63:
        raise HTTPException(status_code=400, detail="Expected 63 landmark features.")

    # Replicate wrist-relative normalization
    wrist_x, wrist_y, wrist_z = data.landmarks[0], data.landmarks[1], data.landmarks[2]
    features = []
    for i in range(21):
        features.extend([
            data.landmarks[i * 3] - wrist_x,
            data.landmarks[i * 3 + 1] - wrist_y,
            data.landmarks[i * 3 + 2] - wrist_z
        ])

    columns = [f'{axis}{i}' for i in range(21) for axis in ['x', 'y', 'z']]
    features_df = pd.DataFrame([features], columns=columns)

    probs = STATIC_MODEL.predict_proba(features_df)[0]
    best_idx = np.argmax(probs)
    raw_class = STATIC_MODEL.classes_[best_idx]

    if STATIC_ENCODER is not None and isinstance(raw_class, (int, np.integer)):
        prediction = STATIC_ENCODER.inverse_transform([raw_class])[0]
    else:
        prediction = str(raw_class)

    return {"prediction": prediction, "confidence": float(probs[best_idx])}


@app.post("/predict/dynamic")
def predict_dynamic(data: DynamicSequenceInput):
    if DYNAMIC_MODEL is None or DYNAMIC_ENCODER is None:
        raise HTTPException(status_code=500, detail="Dynamic model not loaded.")

    seq_array = np.array(data.sequence)
    if seq_array.shape != (SEQUENCE_LENGTH, FEATURE_DIM):
        raise HTTPException(status_code=400, detail=f"Expected shape ({SEQUENCE_LENGTH}, {FEATURE_DIM})")

    input_tensor = torch.tensor(seq_array, dtype=torch.float32).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = DYNAMIC_MODEL(input_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        best_idx = np.argmax(probs)

    prediction = DYNAMIC_ENCODER.inverse_transform([best_idx])[0]
    return {"prediction": prediction, "confidence": float(probs[best_idx])}