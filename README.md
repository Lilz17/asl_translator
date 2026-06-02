# Real-Time ASL to English Translator
This project aims to create a real-time ASL detection system using MediaPipe to handle hand detection and RF/CNN for gesture classification.

Our model is a lightweight ML/CV pipeline that extracts hand landmarks from a live webcam feed or an image/video file and converts them into the respective ASL letters.

We started off with training our model to detect static signs (letters A-Y excluding J). We used a two-stage architecture:
- Mediapipe for feature extraction
- Random Forest Classifier for real-time translation

## System Architecture
1. Feature Extraction: MediaPipe isolates a total of 21 hand landmarks, with each landmark consisting of (X, Y, Z) coordinates for a total of 63 features per frame
2. Relative Scaling: We use the wrist (landmark 0) as our anchor point and subtract its coordinates from all other joints. This relative scaling modification ensures that the system is not affected by varying hand sizes or distances of the hand from the camera lens.
3. Classification: We train a Random Forest Classifier on our image dataset. We then use this pretrained model to evaluate a new image or video's scaled spatial coordinates and predict which letter sign was displayed.

## Repository Files
### Core ML Assets
- `hand_landmarker.task`: This is the official Google MediaPipe Tasks API bundle used to map out hand structures
- `asl_rf_model.pkl`: The frozen weights of our trained Random Forest Classifier model which is saved using `joblib`. We will use this pretrained model for testing its performance on new image/video data.

### Configuration and Testing
- `test_cam.py`: To verify that OpenCV can access the device camera
- `src/data_preprocessing.py`: Evaluates the webcam stream, isolates hands, and prints raw coordinate indices directly to the console.
- `src/data_preprocessing_v2.py`: An upgraded preprocessing script that dynamically draws the skeletal structure (red joint nodes and green skeletal edges) over the detected hand in real time.

### Feature Extraction & Model Training
- `src/image_preprocessing.py`: An automated dataset parser that iterates recursively through directory labels, extracts the relatively normalized landmark coordinates, and saves the flattened matrix arrays directly into asl_landmarks.csv.
- `src/train_model.py`: Loads asl_landmarks.csv, splits features into stratified train/test splits, trains a 100-tree Random Forest engine, and prints out precision metric evaluations.

### Runtime Demonstrations
- `src/demo_webcam.py`: Tests the model on the user's live webcam feed.
- `src/demo_image.py`: Tests the model on a single static image path file.
- `src/demo_video.py`: Tests the model on a standard .mp4 video file or on a YouTube video.

## Installation & Development Workspace
We use `uv` by Astral for version control. `uv` is an extremely fast Python package and project manager written in Rust.

### 1. Create an Environment

```powershell
# Create a new environment with uv
uv venv asl_env --python 3.12

# Activate the environment
asl_env\Scripts\activate
```

### 2. Package Installation

```powershell
uv pip install -r requirements.txt

```
## Current Project Benchmarks

* **Dataset Profile:** 8,243 unique extracted geometric samples across 24 alphabet classes.
* **Pipeline Matrix Precision:** **96.30% overall macro-average accuracy.**

## Future Goals:

* [ ] **Text-to-Speech (TTS):** Integrate an accessibility audio synthesis engine (e.g. `pyttsx3`) to speak out the decoded letters.
* [ ] **Data Augmentation:** Inject artificial spatial noise (jitter transformations) and subtle 2D coordinate rotation matrices into fist-profile signatures (M vs N, S vs T) to sharpen classification boundaries.
* [ ] **React.js Frontend Integration:** Integrate the React.js frontend prototype with our trained model via FastAPI web framework.