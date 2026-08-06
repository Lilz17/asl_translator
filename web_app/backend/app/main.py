import os
import base64
import io
import sys
import numpy as np
import pandas as pd
import joblib
import torch
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
from pathlib import Path
from collections import deque, Counter

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))

from train_Transformer import ASLTransformerClassifier, FEATURE_DIM, SEQUENCE_LENGTH

app = FastAPI(title="ASL Integrated Translation Engine")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = PROJECT_ROOT / "models"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Feature columns matching training DataFrame
FEATURE_NAMES = [f'{axis}{i}' for i in range(21) for axis in ['x', 'y', 'z']]

# Load Static Models
static_model = joblib.load(MODELS_DIR / "asl_static_model.pkl")
static_encoder = joblib.load(MODELS_DIR / "static_label_encoder.pkl")

# Load Dynamic Transformer Model
dynamic_encoder_path = MODELS_DIR / "dynamic_label_encoder.pkl"
dynamic_model_path = MODELS_DIR / "asl_dynamic_transformer.pth"

dynamic_model = None
dynamic_encoder = None
if dynamic_model_path.exists() and dynamic_encoder_path.exists():
    dynamic_encoder = joblib.load(dynamic_encoder_path)
    num_classes = len(dynamic_encoder.classes_)
    dynamic_model = ASLTransformerClassifier(
        input_dim=FEATURE_DIM, d_model=128, nhead=4, num_layers=3, num_classes=num_classes, dropout=0.2
    ).to(DEVICE)
    dynamic_model.load_state_dict(torch.load(dynamic_model_path, map_location=DEVICE, weights_only=True))
    dynamic_model.eval()

# Configure MediaPipe Hand Landmarker
base_options = python.BaseOptions(model_asset_path=str(MODELS_DIR / "hand_landmarker.task"))
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

# Temporal Prediction History Queue for Smoothing
prediction_queue = deque(maxlen=8)

class FramePayload(BaseModel):
    image: Optional[str] = None

class DynamicSequencePayload(BaseModel):
    sequence: List[List[float]]

@app.get("/")
def home():
    return {"message": "ASL Translator Backend Active 🚀", "device": str(DEVICE)}

@app.post("/predict")
def predict_static(payload: FramePayload):
    if not payload.image:
        return {"gesture": None, "confidence": None, "message": "No image received"}

    try:
        image_data = base64.b64decode(payload.image.split(",")[-1])
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        frame = np.array(image)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if not result.hand_landmarks:
            prediction_queue.clear()
            return {"gesture": None, "confidence": None, "message": "No hand detected", "landmarks": []}

        landmarks = result.hand_landmarks[0]
        landmark_list = [{"x": lm.x, "y": lm.y} for lm in landmarks]

        wrist_x, wrist_y, wrist_z = landmarks[0].x, landmarks[0].y, landmarks[0].z

        row = []
        for lm in landmarks:
            row.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])

        # Format features as pandas DataFrame matching training columns
        features_df = pd.DataFrame([row], columns=FEATURE_NAMES)
        probabilities = static_model.predict_proba(features_df)[0]
        best_idx = np.argmax(probabilities)
        confidence = round(float(probabilities[best_idx]) * 100, 1)

        raw_pred = static_model.classes_[best_idx]
        if isinstance(raw_pred, (int, np.integer)):
            predicted_letter = static_encoder.inverse_transform([raw_pred])[0]
        else:
            predicted_letter = str(raw_pred)

        # Apply Temporal Smoothing (Only emit prediction if confidence > 65% and majority agrees)
        if confidence >= 65.0:
            prediction_queue.append(predicted_letter)
        else:
            prediction_queue.append("...")

        # Majority Vote
        vote_counts = Counter(prediction_queue)
        smoothed_gesture, count = vote_counts.most_common(1)[0]

        if smoothed_gesture == "..." or count < 4:
            return {"gesture": None, "confidence": confidence, "landmarks": landmark_list}

        return {"gesture": smoothed_gesture, "confidence": confidence, "landmarks": landmark_list}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict/dynamic")
def predict_dynamic(payload: DynamicSequencePayload):
    if dynamic_model is None or dynamic_encoder is None:
        raise HTTPException(status_code=500, detail="Dynamic Transformer model not initialized.")

    seq_array = np.array(payload.sequence)
    if seq_array.shape != (SEQUENCE_LENGTH, FEATURE_DIM):
        raise HTTPException(status_code=400, detail=f"Expected shape ({SEQUENCE_LENGTH}, {FEATURE_DIM})")

    input_tensor = torch.tensor(seq_array, dtype=torch.float32).unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        logits = dynamic_model(input_tensor)
        probs = torch.softmax(logits, dim=1).cpu().numpy()[0]
        best_idx = np.argmax(probs)

    prediction = dynamic_encoder.inverse_transform([best_idx])[0]
    return {"gesture": str(prediction).upper(), "confidence": round(float(probs[best_idx]) * 100, 1)}