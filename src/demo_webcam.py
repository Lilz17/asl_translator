import cv2
import mediapipe as mp
import time
import joblib
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Load the pre-trained machine learning model weights
MODEL_OUTPUT = 'asl_rf_model.pkl'
rf_model = joblib.load(MODEL_OUTPUT)
print(f"Loaded pre-trained model structural weights from {MODEL_OUTPUT}")

# 2. Configure MediaPipe for sequential live video feed tracking
MODEL_PATH = 'hand_landmarker.task'
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.VIDEO,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.5
)

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

    print("\nLive Demonstration Active! Make an ASL sign in front of the camera.")
    print("Press 'q' to terminate the stream.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the image horizontally for a natural mirror-view experience
        # frame = cv2.flip(frame, 1)
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
                # Add normalized mathematical features to pass to Random Forest
                features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
                
                # Collect screen coordinates for drawing overlays
                pixel_points.append((int(lm.x * w), int(lm.y * h)))
            
            # Pass the 63 flattened relative coordinates into the trained model
            # [features] converts it to a 2D array shape (1, 63) expected by scikit-learn
            prediction = rf_model.predict([features])[0]
            
            # Fetch confidence probabilities to display how sure the model is
            probabilities = rf_model.predict_proba([features])[0]
            max_prob = max(probabilities) * 100

            # Draw a clean UI boundary text container on the live OpenCV frame
            display_text = f"Predicted Sign: {prediction} ({max_prob:.1f}%)"
            
            # Render a green text box if confidence is high, red if shaky
            color = (0, 255, 0) if max_prob > 75 else (0, 0, 255)
            cv2.putText(frame, display_text, (30, 60), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, color, 3)

            # Draw basic joint tracking points onto screen
            # for pt in pixel_points:
            #     cv2.circle(frame, pt, 4, (255, 0, 0), -1)

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