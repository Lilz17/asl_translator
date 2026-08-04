import cv2
import joblib
import torch
import numpy as np
import mediapipe as mp
from collections import deque
from pathlib import Path
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from train_GRU_CNN import ConvGRUClassifier

# ==========================================
# Config & Paths
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODEL_PATH = PROJECT_ROOT / "models" / "asl_dynamic_gru.pth"
ENCODER_PATH = PROJECT_ROOT / "models" / "dynamic_label_encoder.pkl"
TASK_PATH = PROJECT_ROOT / "models" / "hand_landmarker.task"

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
SEQUENCE_LENGTH = 30
FEATURE_DIM = 63

# Skeleton Connections (Pairs of landmark indices)
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),        # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),        # Index
    (9, 10), (10, 11), (11, 12),           # Middle
    (13, 14), (14, 15), (15, 16),          # Ring
    (0, 17), (17, 18), (18, 19), (19, 20), # Pinky
    (5, 9), (9, 13), (13, 17)              # Palm
]

label_encoder = joblib.load(ENCODER_PATH)
num_classes = len(label_encoder.classes_)

model = ConvGRUClassifier(
    input_dim=63,
    hidden_dim=128,
    num_layers=2,
    num_classes=len(label_encoder.classes_),  # This automatically accounts for 'neutral' now!
    dropout=0.3
).to(DEVICE)

model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE, weights_only=True))
model.eval()


def draw_skeleton(frame, landmarks, w, h):
    """Draws red joints and green skeleton lines."""
    coords = [(int(lm.x * w), int(lm.y * h)) for lm in landmarks]
    for p1, p2 in HAND_CONNECTIONS:
        cv2.line(frame, coords[p1], coords[p2], (0, 255, 0), 2)
    for pt in coords:
        cv2.circle(frame, pt, 4, (0, 0, 255), -1)


def process_video(video_path):
    base_options = python.BaseOptions(model_asset_path=str(TASK_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.2
    )

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        print(f"Could not open video file: {video_path}")
        return

    frame_buffer = deque(maxlen=SEQUENCE_LENGTH)

    with vision.HandLandmarker.create_from_options(options) as detector:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            res = detector.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))

            pred_text = "Predicted Sign: None"

            if res.hand_landmarks:
                landmarks = res.hand_landmarks[0]
                wx, wy, wz = landmarks[0].x, landmarks[0].y, landmarks[0].z

                frame_feats = []
                for pt in landmarks:
                    frame_feats.extend([pt.x - wx, pt.y - wy, pt.z - wz])

                draw_skeleton(frame, landmarks, w, h)
                frame_buffer.append(frame_feats)

                if len(frame_buffer) == SEQUENCE_LENGTH:
                    seq_arr = np.array(frame_buffer)
                    tensor_in = torch.tensor(seq_arr, dtype=torch.float32).unsqueeze(0).to(DEVICE)

                    with torch.no_grad():
                        logits = model(tensor_in)
                        probs = torch.softmax(logits, dim=1)
                        pred_idx = torch.argmax(probs, dim=1).item()
                        conf = probs[0][pred_idx].item() * 100

                    # Requiring high confidence to filter out idle states
                    if conf > 85.0:
                        pred_label = label_encoder.inverse_transform([pred_idx])[0]
                        pred_text = f"Predicted Sign: {pred_label.upper()} ({conf:.1f}%)"
            else:
                frame_buffer.clear()

            # Overlay
            cv2.putText(frame, pred_text, (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.imshow("ASL Dynamic Video Test", frame)

            if cv2.waitKey(30) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    test_video = input("Enter path to a test MP4/AVI video file: ").strip().strip('"')
    process_video(test_video)