import os
import csv
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision

# Setup paths
DATASET_PATH = 'dataset/ASL_Static/SigNN Character Database/'
OUTPUT_CSV = 'asl_landmarks.csv'
MODEL_PATH = 'hand_landmarker.task'

# Configure MediaPipe for Static Images
base_options = python.BaseOptions(model_asset_path=MODEL_PATH)
options = vision.HandLandmarkerOptions(
    base_options=base_options,
    running_mode=vision.RunningMode.IMAGE,
    num_hands=1
)

# a hand has 21 landmarks, so we will have 63 columns for the coordinates (x, y, z) plus one for the label

# Generate CSV Header: label, x0, y0, z0, x1, y1, z1 ... up to z20
csv_header = ['label']
for i in range(21):
    csv_header.extend([f'x{i}', f'y{i}', f'z{i}'])

# Open CSV and begin looping through folders
with open(OUTPUT_CSV, mode='w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(csv_header)  # Write our column headers

    # Initialize the MediaPipe detector container
    with vision.HandLandmarker.create_from_options(options) as detector:
                
        # Browse through subfolders (A, B, C...) and gather image files
        target_labels = sorted([d for d in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, d))])
        
        print(f"Found target labels for processing: {target_labels}")

        # For each image, run it through the MediaPipe graph to extract hand landmarks
        for label in target_labels:
            label_path = os.path.join(DATASET_PATH, label)
            image_files = [img for img in os.listdir(label_path) if img.lower().endswith(('.png', '.jpg', '.jpeg'))]
            
            print(f"Processing label '{label}': Extracting from {len(image_files)} images...")

            for img_file in image_files:
                img_path = os.path.join(label_path, img_file)
                
                # Load image via OpenCV
                frame = cv2.imread(img_path)

                # Exception Handling (Check if the image is corrupted or unreadable)
                if frame is None:
                    print(f"Warning: Could not read image {img_path}. Skipping.")
                    continue
                
                # Convert and wrap for MediaPipe graph execution
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)
                
                # Execute Inference
                detection_result = detector.detect(mp_image)
                
                # Exception Handling (Check if a hand was found)
                if not detection_result.hand_landmarks:
                    # No hand found = skip this image and move on to the next one
                    print(f"No hand detected in {img_path}. Skipping.")
                    continue 
                
                # Hand found = extract landmarks and write to CSV
                landmarks = detection_result.hand_landmarks[0]
                
                # We will use the wrist (landmark 0) as our anchor point for relative coordinates to improve model robustness against hand position variance
                wrist_x = landmarks[0].x
                wrist_y = landmarks[0].y
                wrist_z = landmarks[0].z # Normalizing depth relative to the wrist
                
                # Building the flattened row data profile
                row_data = [label]
                
                for lm in landmarks:
                    # Calculate the relative coordinates of each landmark to the wrist
                    relative_x = lm.x - wrist_x
                    relative_y = lm.y - wrist_y
                    relative_z = lm.z - wrist_z
                    
                    # append the resulting coordinates to the row data list
                    row_data.extend([relative_x, relative_y, relative_z])
                
                # Save the row to the CSV file
                writer.writerow(row_data)