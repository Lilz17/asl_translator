import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

model_path = 'models/hand_landmarker.task'
base_options = python.BaseOptions(model_asset_path=model_path)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=2,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5
)

# Crucial MediaPipe connection map: tells us which landmark connect to which (e.g., wrist to thumb)
# There are 21 landmarks total per hand
HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),      # Index Finger
    (9, 10), (10, 11), (11, 12),         # Middle Finger (starts from 5/9 connection)
    (13, 14), (14, 15), (15, 16),        # Ring Finger
    (0, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (5, 9), (9, 13), (13, 17)            # Palm baseline connections
]

with vision.HandLandmarker.create_from_options(options) as detector:
    cap = cv2.VideoCapture(0)

    print("Visual Tasks API Tracker active. Press 'q' to close camera stream.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape # Get height and width of frame to unpack normalized points
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        frame_timestamp_ms = int(time.time() * 1000)

        detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

        if detection_result.hand_landmarks:
            for landmarks in detection_result.hand_landmarks:

                # Print the wrist coordinates to the terminal
                wrist = landmarks[0]
                print(f"Wrist Coordinates -> X: {wrist.x:.2f}, Y: {wrist.y:.2f}, Z: {wrist.z:.2f}")
                
                # 1. Convert normalized floats (0.0 - 1.0) to actual image pixel coordinates
                pixel_points = []
                for lm in landmarks:
                    px_x, px_y = int(lm.x * w), int(lm.y * h)
                    pixel_points.append((px_x, px_y))
                
                # 2. Draw the skeletal bones (lines) connecting the joints
                for connection in HAND_CONNECTIONS:
                    start_idx, end_idx = connection
                    cv2.line(frame, pixel_points[start_idx], pixel_points[end_idx], (0, 255, 0), 2) # Green Lines

                # 3. Draw the joint tracking markers (dots)
                for pt in pixel_points:
                    cv2.circle(frame, pt, 5, (0, 0, 255), -1) # Red Dots

        cv2.imshow('MediaPipe Tasks API - Wireframe View', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()