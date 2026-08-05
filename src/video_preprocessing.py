import os
import cv2
import numpy as np
from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# ==========================================
# Paths Configuration
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Pointing to your actual raw video dataset folder
RAW_VIDEOS_DIR = PROJECT_ROOT / "dataset" / "ASL_Dynamic"
OUTPUT_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Extracted"
HAND_LANDMARKER_PATH = PROJECT_ROOT / "models" / "hand_landmarker.task"

SEQUENCE_LENGTH = 30
FEATURE_DIM = 66  # 60 finger features + 3 wrist coords + 3 velocity terms


def extract_features_from_video(video_path, detector):
    cap = cv2.VideoCapture(str(video_path))
    raw_frames = []
    
    prev_wrist = None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        detection_result = detector.detect(mp_image)

        if detection_result.hand_landmarks:
            landmarks = detection_result.hand_landmarks[0]
            wrist_x, wrist_y, wrist_z = landmarks[0].x, landmarks[0].y, landmarks[0].z

            # Calculate Frame-to-Frame Velocity
            if prev_wrist is None:
                vx, vy, vz = 0.0, 0.0, 0.0
            else:
                vx = wrist_x - prev_wrist[0]
                vy = wrist_y - prev_wrist[1]
                vz = wrist_z - prev_wrist[2]
            
            prev_wrist = (wrist_x, wrist_y, wrist_z)

            # Wrist-relative finger landmarks (60 features)
            finger_features = []
            for lm in landmarks[1:]:
                finger_features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])

            # Wrist absolute position (3 features) + Velocity (3 features)
            anchor_features = [wrist_x, wrist_y, wrist_z, vx, vy, vz]

            frame_features = finger_features + anchor_features
            raw_frames.append(frame_features)

    cap.release()

    if len(raw_frames) < 10:
        return None  # Skip corrupted or overly short videos

    # Temporal Resampling to exact 30 frames
    raw_array = np.array(raw_frames)
    total_frames = len(raw_array)
    original_indices = np.linspace(0, total_frames - 1, num=total_frames)
    target_indices = np.linspace(0, total_frames - 1, num=SEQUENCE_LENGTH)

    resampled = np.zeros((SEQUENCE_LENGTH, FEATURE_DIM))
    for col in range(FEATURE_DIM):
        resampled[:, col] = np.interp(target_indices, original_indices, raw_array[:, col])

    return resampled


def main():
    if not RAW_VIDEOS_DIR.exists():
        raise FileNotFoundError(
            f"Cannot find dataset directory at: {RAW_VIDEOS_DIR.resolve()}\n"
            f"Please ensure your raw videos are placed inside 'dataset/ASL_Dynamic'."
        )

    if not HAND_LANDMARKER_PATH.exists():
        raise FileNotFoundError(f"Missing hand landmarker model at {HAND_LANDMARKER_PATH.resolve()}")

    base_options = python.BaseOptions(model_asset_path=str(HAND_LANDMARKER_PATH))
    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        running_mode=vision.RunningMode.IMAGE,
        num_hands=1,
        min_hand_detection_confidence=0.3
    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    with vision.HandLandmarker.create_from_options(options) as detector:
        for class_folder in [f for f in RAW_VIDEOS_DIR.iterdir() if f.is_dir()]:
            class_name = class_folder.name
            target_class_dir = OUTPUT_DIR / class_name
            target_class_dir.mkdir(parents=True, exist_ok=True)

            print(f"Processing class: '{class_name}' into 66 spatial features...")
            
            # Check for mp4/avi files
            video_files = list(class_folder.glob("*.mp4")) + list(class_folder.glob("*.avi"))
            for vid_file in video_files:
                seq = extract_features_from_video(vid_file, detector)
                if seq is not None:
                    out_path = target_class_dir / f"{vid_file.stem}.npy"
                    np.save(out_path, seq)

    print(f"\nLandmark extraction completed! Output saved to {OUTPUT_DIR}.")


if __name__ == "__main__":
    main()