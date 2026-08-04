from collections import deque, Counter
import cv2
import joblib
import numpy as np
from pathlib import Path
import torch
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

import sys
from pathlib import Path

from train_Transformer import ASLTransformerClassifier

# Configurations
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.append(str(PROJECT_ROOT / "src"))
MODELS_DIR = PROJECT_ROOT / "models"

MODEL_PATH = MODELS_DIR / "asl_dynamic_transformer.pth"
LABEL_ENCODER_PATH = MODELS_DIR / "dynamic_label_encoder.pkl"
HAND_LANDMARKER_PATH = MODELS_DIR / "hand_landmarker.task"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEQUENCE_LENGTH = 30
FEATURE_DIM = 66

# --- DEPLOYMENT SMOOTHING HYPERPARAMETERS ---
CONFIDENCE_THRESHOLD = 0.80     # Required confidence score
SMOOTHING_WINDOW = 10           # Number of frames to hold in voting queue
VOTE_THRESHOLD = 7              # Minimum agreement count (e.g., 5 out of 7 frames)
MAX_TRANSITION_VELOCITY = 0.08  # Wrist speed limit to prevent mid-transition guessing

HAND_CONNECTIONS = [
    (0,1), (1,2), (2,3), (3,4),       # Thumb
    (0,5), (5,6), (6,7), (7,8),       # Index
    (5,9), (9,10), (10,11), (11,12),  # Middle
    (9,13), (13,14), (14,15), (15,16),# Ring
    (13,17), (0,17), (17,18), (18,19), (19,20) # Pinky
]


def resample_sequence(raw_sequence, target_length=30):
    total_frames = len(raw_sequence)
    if total_frames == target_length:
        return np.array(raw_sequence)

    original_indices = np.linspace(0, total_frames - 1, num=total_frames)
    target_indices = np.linspace(0, total_frames - 1, num=target_length)

    raw_array = np.array(raw_sequence)
    resampled = np.zeros((target_length, FEATURE_DIM))
    for col in range(FEATURE_DIM):
        resampled[:, col] = np.interp(target_indices, original_indices, raw_array[:, col])

    return resampled


def draw_skeleton(image, landmarks_list):
    h, w, _ = image.shape
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks_list]

    for p1, p2 in HAND_CONNECTIONS:
        cv2.line(image, coords[p1], coords[p2], (0, 255, 0), 2)
    for pt in coords:
        cv2.circle(image, pt, 4, (0, 0, 255), -1)


def main():
    if not MODEL_PATH.exists() or not LABEL_ENCODER_PATH.exists():
        print("Missing model or encoder. Train first!")
        return

    label_encoder = joblib.load(LABEL_ENCODER_PATH)
    num_classes = len(label_encoder.classes_)

    model = ASLTransformerClassifier(
        input_dim=FEATURE_DIM, d_model=128, nhead=4, num_layers=3, num_classes=num_classes, dropout=0.2
    ).to(DEVICE)

    model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
    model.eval()

    base_options = python.BaseOptions(model_asset_path=str(HAND_LANDMARKER_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.3
    )

    cap = cv2.VideoCapture(0)
    frame_buffer = []
    prediction_history = deque(maxlen=SMOOTHING_WINDOW)
    prev_wrist = None

    print("Starting Stabilized WebCam Demo. Press 'q' to quit.")

    with vision.HandLandmarker.create_from_options(options) as detector:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            frame = cv2.flip(frame, 1)
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

            detection_result = detector.detect(mp_image)

            if detection_result.hand_landmarks:
                landmarks = detection_result.hand_landmarks[0]
                wrist_x, wrist_y, wrist_z = landmarks[0].x, landmarks[0].y, landmarks[0].z

                # Velocity calculation
                if prev_wrist is None:
                    vx, vy, vz = 0.0, 0.0, 0.0
                else:
                    vx = wrist_x - prev_wrist[0]
                    vy = wrist_y - prev_wrist[1]
                    vz = wrist_z - prev_wrist[2]
                prev_wrist = (wrist_x, wrist_y, wrist_z)

                speed = np.sqrt(vx**2 + vy**2 + vz**2)

                # Feature Assembly
                finger_features = []
                for lm in landmarks[1:]:
                    finger_features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])

                anchor_features = [wrist_x, wrist_y, wrist_z, vx, vy, vz]
                frame_features = finger_features + anchor_features

                frame_buffer.append(frame_features)
                if len(frame_buffer) > 40:
                    frame_buffer.pop(0)

                draw_skeleton(frame, landmarks)

            else:
                frame_buffer.clear()
                prediction_history.clear()
                prev_wrist = None
                speed = 0.0

            # --- PREDICTION & SMOOTHING LOGIC ---
            if len(frame_buffer) >= 18:
                input_sequence = resample_sequence(frame_buffer, SEQUENCE_LENGTH)
                input_tensor = torch.tensor(input_sequence, dtype=torch.float32).unsqueeze(0).to(DEVICE)

                with torch.no_grad():
                    logits = model(input_tensor)
                    probabilities = torch.softmax(logits, dim=1)
                    confidence, pred_class_idx = torch.max(probabilities, dim=1)

                raw_label = label_encoder.inverse_transform([pred_class_idx.item()])[0]
                conf_score = confidence.item()

                # Filter out low confidence or neutral
                if raw_label != "neutral" and conf_score >= CONFIDENCE_THRESHOLD:
                    prediction_history.append(raw_label)
                else:
                    prediction_history.append("idle")

                # Majority Vote over recent predictions
                vote_counts = Counter(prediction_history)
                most_common_label, highest_votes = vote_counts.most_common(1)[0]

                if most_common_label != "idle" and highest_votes >= VOTE_THRESHOLD:
                    display_text = f"Sign: {most_common_label.upper()} ({conf_score * 100:.0f}%)"
                    color = (0, 255, 0)
                    bg_color = (0, 70, 0)
                elif speed > MAX_TRANSITION_VELOCITY:
                    display_text = "Status: Analyzing Motion..."
                    color = (0, 215, 255)
                    bg_color = (0, 50, 60)
                else:
                    display_text = "Status: Ready / Listening"
                    color = (180, 180, 180)
                    bg_color = (40, 40, 40)

                cv2.rectangle(frame, (10, 10), (460, 60), bg_color, -1)
                cv2.rectangle(frame, (10, 10), (460, 60), color, 2)
                cv2.putText(frame, display_text, (20, 45), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

            else:
                cv2.rectangle(frame, (10, 10), (350, 60), (30, 30, 30), -1)
                cv2.putText(frame, "Status: Buffer Building...", (20, 45),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.65, (200, 200, 200), 2)

            cv2.imshow("ASL Dynamic Transformer Recognition", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()