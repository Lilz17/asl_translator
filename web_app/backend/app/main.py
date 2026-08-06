import os
import base64
import io
import numpy as np
import joblib
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from PIL import Image
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MODELS_DIR = r"D:\project\asl_translator\models"
model = joblib.load(os.path.join(MODELS_DIR, "asl_static_model.pkl"))
label_encoder = joblib.load(os.path.join(MODELS_DIR, "static_label_encoder.pkl"))

base_options = python.BaseOptions(
    model_asset_path=os.path.join(MODELS_DIR, "hand_landmarker.task")
)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1
)
detector = vision.HandLandmarker.create_from_options(options)

class FramePayload(BaseModel):
    image: Optional[str] = None

@app.get("/")
def home():
    return {"message": "ASL Backend Running 🚀"}

@app.post("/predict")
def predict(payload: FramePayload):
    if not payload.image:
        print("No image received")
        return {"gesture": None, "confidence": None, "message": "No image received"}

    try:
        image_data = base64.b64decode(payload.image.split(",")[-1])
        image = Image.open(io.BytesIO(image_data)).convert("RGB")
        frame = np.array(image)

        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
        result = detector.detect(mp_image)

        if not result.hand_landmarks:
            print("No hand detected")
            return {"gesture": None, "confidence": None, "message": "No hand detected", "landmarks": []}

        landmarks = result.hand_landmarks[0]
        landmark_list = [{"x": lm.x, "y": lm.y} for lm in landmarks]

        wrist_x = landmarks[0].x
        wrist_y = landmarks[0].y
        wrist_z = landmarks[0].z

        row = []
        for lm in landmarks:
            row.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])

        features = np.array(row).reshape(1, -1)
        prediction = model.predict(features)[0]
        probabilities = model.predict_proba(features)[0]
        confidence = round(float(np.max(probabilities)) * 100, 1)
        gesture = label_encoder.inverse_transform([prediction])[0]

        print(f"Detected: {gesture} ({confidence}%)")

        return {"gesture": gesture, "confidence": confidence, "landmarks": landmark_list}

    except Exception as e:
        print(f"ERROR: {e}")
        raise HTTPException(status_code=500, detail=str(e))