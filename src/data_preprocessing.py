import cv2
import mediapipe as mp
import time
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# STEP 1: Define model configuration options
model_path = 'hand_landmarker.task'
base_options = python.BaseOptions(model_asset_path=model_path)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO, # Configured for video stream sequences
    num_hands=2,
    min_hand_detection_confidence=0.7,     # Strictness threshold for initial detection
    min_hand_presence_confidence=0.5
)

# STEP 2: Initialize the detector inside a context manager
with vision.HandLandmarker.create_from_options(options) as detector:
    cap = cv2.VideoCapture(0)  # Safe for Iriun Phone Camera feed

    print("Tasks API Hand Tracking Online. Press 'q' to exit.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Convert the frame format from BGR to RGB for MediaPipe
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert the frame array into a native MediaPipe Image wrapper
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
        
        # The Tasks API requires a monotonically increasing timestamp in milliseconds
        frame_timestamp_ms = int(time.time() * 1000)

        # STEP 3: Run inference on the current sequential frame
        detection_result = detector.detect_for_video(mp_image, frame_timestamp_ms)

        # STEP 4: Access and parse the tracked landmark positions
        if detection_result.hand_landmarks:
            for hand_idx, landmarks in enumerate(detection_result.hand_landmarks):
                # Sample output: Track the position of your Wrist joint (Index 0)
                wrist = landmarks[0]
                
                # Render basic text on the camera window for visual confirmation
                cv2.putText(frame, f"Tracking Hand {hand_idx+1}", (30, 50 + (hand_idx * 40)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                
                # Print coordinates to verify data streams are alive
                print(f"Hand {hand_idx}: Wrist X={wrist.x:.2f}, Y={wrist.y:.2f}")

        # Display the output window
        cv2.imshow('MediaPipe Tasks API Live Feed', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()