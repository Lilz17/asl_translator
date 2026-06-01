import sys
import os
import time
import cv2
import joblib
import warnings
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import yt_dlp

# Mute warnings so they do not clutter the terminal
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# 1. Choose Input: Accept a local video file, a YouTube link, or fallback to default
if len(sys.argv) > 1:
    INPUT_TARGET = sys.argv[1]
else:
    # Default fallback: paste a YouTube link or a local path here to test quickly
    INPUT_TARGET = 'https://www.youtube.com/watch?v=eeAq4gkOEUY'  # Example YouTube video with ASL content

# 2. Load ML components
MODEL_OUTPUT = 'asl_rf_model.pkl'
rf_model = joblib.load(MODEL_OUTPUT)
MODEL_PATH = 'hand_landmarker.task'

base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.6 # Slightly lower confidence threshold helps with fast video movement
)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4), (0, 5), (5, 6), (6, 7), (7, 8),
    (9, 10), (10, 11), (11, 12), (13, 14), (14, 15), (15, 16),
    (0, 17), (17, 18), (18, 19), (19, 20), (5, 9), (9, 13), (13, 17)
]

# 3. Handle YouTube Links vs Local Files
is_youtube = "youtube.com" in INPUT_TARGET or "youtu.be" in INPUT_TARGET

if is_youtube:
    print(f"Extracting live stream URL from YouTube link...")
    ydl_opts = {'format': 'best[ext=mp4]', 'quiet': True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(INPUT_TARGET, download=False)
        video_stream_url = info['url']
    cap = cv2.VideoCapture(video_stream_url)
else:
    if not os.path.exists(INPUT_TARGET):
        print(f"Error: Video file not found at '{INPUT_TARGET}'")
        sys.exit(1)
    cap = cv2.VideoCapture(INPUT_TARGET)

with vision.HandLandmarker.create_from_options(options) as detector:
    print("\nProcessing Video Stream... Press 'q' inside the video window to quit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Video stream ended or completed.")
            break

        # if video is massive -> Resize down
        # 4K/1080p can lag MediaPipe loops
        if frame.shape[1] > 1000:
            frame = cv2.resize(frame, (960, 540))

        h, w, _ = frame.shape
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # Calculate sequential timestamps relative to current video frame positioning
        frame_timestamp_ms = int(cap.get(cv2.CAP_PROP_POS_MSEC))

        detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

        if detection_result.hand_landmarks:
            landmarks = detection_result.hand_landmarks[0]
            wrist_x, wrist_y, wrist_z = landmarks[0].x, landmarks[0].y, landmarks[0].z
            
            features = []
            pixel_points = []
            
            for lm in landmarks:
                features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
                pixel_points.append((int(lm.x * w), int(lm.y * h)))
            
            # Predict
            prediction = rf_model.predict([features])[0]
            probabilities = rf_model.predict_proba([features])[0]
            max_prob = max(probabilities) * 100

            # UI Text Overlay
            display_text = f"ASL Sign: {prediction} ({max_prob:.1f}%)"
            color = (0, 255, 0) if max_prob > 70 else (0, 0, 255)
            cv2.putText(frame, display_text, (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 3)

            # Render Skeleton wireframe over video frame
            for connection in HAND_CONNECTIONS:
                cv2.line(frame, pixel_points[connection[0]], pixel_points[connection[1]], (0, 255, 0), 2)
            for pt in pixel_points:
                cv2.circle(frame, pt, 4, (0, 0, 255), -1)

        cv2.imshow('ASL Video Translation Interface', frame)
        
        # Sync video playback speeds to keep it natural
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()