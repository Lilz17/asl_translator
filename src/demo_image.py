import sys
import os
import cv2
import mediapipe as mp
import joblib
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# 1. Verification check: pass image via command line or use a default fallback
if len(sys.argv) > 1:
    IMAGE_PATH = sys.argv[1]
else:
    # Fallback to a placeholder path if you just run the script directly
    IMAGE_PATH = 'dataset/ASL_Static/SigNN Character Database/A/1.jpg' 

if not os.path.exists(IMAGE_PATH):
    print(f"Error: Target image file not found at '{IMAGE_PATH}'")
    sys.exit(1)

# 2. Load the pre-trained Random Forest model structure
MODEL_OUTPUT = 'models/asl_rf_model.pkl'
rf_model = joblib.load(MODEL_OUTPUT)
print(f"Loaded pre-trained model weights from {MODEL_OUTPUT}")

# 3. Configure MediaPipe for Static Image mode processing
MODEL_PATH = 'models/hand_landmarker.task'
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE, # Static frame evaluation
    num_hands=1
)

HAND_CONNECTIONS = [
    (0, 1), (1, 2), (2, 3), (3, 4),      # Thumb
    (0, 5), (5, 6), (6, 7), (7, 8),      # Index Finger
    (9, 10), (10, 11), (11, 12),         # Middle Finger
    (13, 14), (14, 15), (15, 16),        # Ring Finger
    (0, 17), (17, 18), (18, 19), (19, 20),# Pinky
    (5, 9), (9, 13), (13, 17)            # Palm baseline connections
]

with vision.HandLandmarker.create_from_options(options) as detector:
    # Read target image via OpenCV
    frame = cv2.imread(IMAGE_PATH)
    h, w, _ = frame.shape

    # Convert format for MediaPipe backend graph execution
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

    print(f"Analyzing structure for: {IMAGE_PATH}")
    detection_result = detector.detect(mp_image)

    if detection_result.hand_landmarks:
        landmarks = detection_result.hand_landmarks[0]
        
        # Pull anchor offsets for relative alignment math
        wrist_x = landmarks[0].x
        wrist_y = landmarks[0].y
        wrist_z = landmarks[0].z
        
        features = []
        pixel_points = []
        
        for lm in landmarks:
            # Replicate the exact mathematical transformation used in your training data
            features.extend([lm.x - wrist_x, lm.y - wrist_y, lm.z - wrist_z])
            pixel_points.append((int(lm.x * w), int(lm.y * h)))
            
        # Run calculation inferences via Scikit-Learn
        prediction = rf_model.predict([features])[0]
        probabilities = rf_model.predict_proba([features])[0]
        max_prob = max(probabilities) * 100

        # Draw UI overlay texts and skeletal frames onto the matrix container
        display_text = f"Predicted Sign: {prediction} ({max_prob:.1f}%)"
        color = (0, 255, 0) if max_prob > 75 else (0, 0, 255)
        
        cv2.putText(frame, display_text, (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, color, 2)

        # Render Bones (Green)
        for connection in HAND_CONNECTIONS:
            start_idx, end_idx = connection
            cv2.line(frame, pixel_points[start_idx], pixel_points[end_idx], (0, 255, 0), 2)

        # Render Joints (Red)
        for pt in pixel_points:
            cv2.circle(frame, pt, 5, (0, 0, 255), -1)
            
        print(f"Result -> {display_text}")
    else:
        cv2.putText(frame, "No Hand Detected", (30, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 0, 255), 2)
        print("Inference Failed: MediaPipe could not locate a clear hand target profile.")
    
    # Allow the window to be manually or automatically resized
    cv2.namedWindow('ASL Static Image Evaluation Engine', cv2.WINDOW_NORMAL)
    
    # Scale down the image if it exceeds comfortable screen dimensions
    max_display_width = 1000
    max_display_height = 800
    
    display_h, display_w, _ = frame.shape
    if display_w > max_display_width or display_h > max_display_height:
        # Calculate scaling ratio to keep the original aspect ratio perfect
        scaling_factor = min(max_display_width / display_w, max_display_height / display_h)
        new_w = int(display_w * scaling_factor)
        new_h = int(display_h * scaling_factor)
        frame = cv2.resize(frame, (new_w, new_h))

    # Show the scaled image
    print("Displaying output window. Press any key on your keyboard to close it.")
    cv2.imshow('ASL Static Image Evaluation Engine', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()