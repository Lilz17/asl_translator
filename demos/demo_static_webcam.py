import cv2
import mediapipe as mp
import time
import joblib
import pandas as pd
import numpy as np
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import os

# Project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_OUTPUT = os.path.join(BASE_DIR, 'models', 'asl_static_model.pkl')
MODEL_PATH = os.path.join(BASE_DIR, 'models', 'hand_landmarker.task')
LABEL_ENCODER_PATH = os.path.join(BASE_DIR, 'models', 'static_label_encoder.pkl')

# Load the pre-trained machine learning model weights & optional Label Encoder
model = joblib.load(MODEL_OUTPUT)
label_encoder = joblib.load(LABEL_ENCODER_PATH) if os.path.exists(LABEL_ENCODER_PATH) else None

print(f"Loaded pre-trained model structural weights from {MODEL_OUTPUT}")

# Pre-define feature column names matching your training DataFrame (x0, y0, z0 ... z20)
FEATURE_NAMES = [f'{axis}{i}' for i in range(21) for axis in ['x', 'y', 'z']]

# Configure MediaPipe for sequential live video feed tracking
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5
)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index Finger
    (9, 10), (10, 11), (11, 12),           # Middle Finger
    (13, 14), (14, 15), (15, 16),          # Ring Finger
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm baseline connections
]

with vision.HandLandmarker.create_from_options(options) as detector:
    cap = cv2.VideoCapture(0)

    print("\nLive Demonstration Active! Make an ASL sign in front of the camera.")
    print("Press 'q' to terminate the stream.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the image horizontally for a natural mirror-view experience
        frame = cv2.flip(frame, 1)
        h, w, _ = frame.shape
        
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        frame_timestamp_ms = int(time.time() * 1000)

        # Run Live Frame Tracking Inference
        detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

        if detection_result.hand_landmarks:
            landmarks = detection_result.hand_landmarks[0]
            
            # Extract absolute anchor offsets
            wrist_x = landmarks[0].x
            wrist_y = landmarks[0].y
            wrist_z = landmarks[0].z
            
            # Construct feature array profile
            features = []
            pixel_points = []
            
            for lm in landmarks:
                # Add normalized mathematical features to pass to trained model
                features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
                
                # Collect screen coordinates for drawing overlays
                pixel_points.append((int(lm.x * w), int(lm.y * h)))
            
            # Wrap feature list in a DataFrame with matching column names
            features_df = pd.DataFrame([features], columns=FEATURE_NAMES)

            # Fetch confidence probabilities
            probabilities = model.predict_proba(features_df)[0]
            best_idx = np.argmax(probabilities)
            max_prob = probabilities[best_idx] * 100

            # Map the index back to the letter ('A'-'Z')
            if label_encoder is not None:
                predicted_sign = label_encoder.inverse_transform([best_idx])[0]
            else:
                predicted_sign = model.classes_[best_idx]

            # Draw a clean UI boundary text container on the live OpenCV frame
            display_text = f"Predicted Sign: {predicted_sign} ({max_prob:.1f}%)"
            
            # Render a green text box if confidence is high (above 75%) else red
            color = (0, 255, 0) if max_prob > 75 else (0, 0, 255)
            cv2.putText(frame, display_text, (30, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            # Draw the skeletal bones (lines) connecting the joints
            for connection in HAND_CONNECTIONS:
                start_idx, end_idx = connection
                cv2.line(frame, pixel_points[start_idx], pixel_points[end_idx], (0, 255, 0), 2)

            # Draw the joint tracking markers (dots)
            for pt in pixel_points:
                cv2.circle(frame, pt, 5, (0, 0, 255), -1)

        cv2.imshow('ASL Real-Time Translation Engine', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()