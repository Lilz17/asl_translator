
# Real-Time American Sign Language (ASL) Recognition Engine

An end-to-end Machine Learning and Computer Vision framework for translating American Sign Language (ASL) in real time. The system features a dual-architecture engine capable of recognizing Static Alphabet Signs ($A$–$Y$, excl. $J$) using spatial keypoint alignment and Dynamic Gesture Sequences using a Spatial-Temporal Transformer.


## System Architecture

```
                                ┌─ Static (21 Keypoints / 63 Dim)  ──► SVM Classifier ─────────► Letter ('A'-'Y' (minus 'J'))
[ Frame / Video ] ──► MediaPipe ┤
                                └─ Dynamic (30 Frames / 66 Dim)   ──► Spatial-Temporal Transformer ──► Word ('J', 'Z', 'HELLO', etc.)
```

1. **Feature Extraction**: MediaPipe Hand Landmarker extracts 21 3D hand keypoints ($x, y, z$), yielding 63 spatial features per frame.
2. **Wrist-Relative Normalization**: All joint coordinates are calculated relative to the wrist anchor ($lm_0$). This mathematical alignment guarantees scale and positional invariance regardless of hand distance or frame position.
3. **Static Classification**: Evaluates normalized static frame vectors through an optimized Support Vector Machine (SVM).
4. **Dynamic Sequence Translation**: Processes 30-frame temporal landmark sequences (including velocity components $v_x, v_y, v_z$) using a 3-layer Spatial-Temporal Transformer with multi-head self-attention.
5. **Full-Stack Deployment**: Exposes inference endpoints via a FastAPI microservice consumed by a modern React + Vite web application.
## Prerequisites & Installation

### System Dependencies

- **Python**: 3.10+

- **Node.js & npm**: Required for the web interface. On macOS, install via Homebrew if missing:

```bash
brew install node
```

- **OpenMP (macOS only)**: Required by XGBoost on Apple Silicon:

```bash
brew install libomp
```

### Environment Setup (`uv`)

We use [uv](https://github.com/astral-sh/uv) for fast, reliable package management.

```bash
# 1. Clone repository
git clone https://github.com/Lilz17/asl_translator.git
cd asl_translator

# 2. Create virtual environment
uv venv asl_env

# 3. Activate environment
# macOS / Linux:
source asl_env/bin/activate
# Windows:
asl_env\Scripts\activate

# 4. Install Python dependencies
uv pip install -r requirements.txt
```
## Dataset Directory Preparation

Before running training pipelines, extract your dataset archives into a root `/dataset/` directory:

```
asl_translator/
└── dataset/
    ├── ASL_Static/             # Extracted static image folders ('A' through 'Y' excluding 'J')
    └── ASL_Dynamic_FULL/       # Raw dynamic video clip directories
```
## Pipeline Execution & Model Training

### 1. Static Sign Model Pipeline ($A$–$Z$)

```bash
# Extract normalized spatial coordinates from images -> data/asl_landmarks.csv
python src/image_preprocessing.py

# Train baseline Random Forest model
python src/train_static_baseline.py

# Generate spatial jitter augmentations -> data/asl_landmarks_augmented.csv
python src/augment_data_static.py

# Train & compare RF, XGBoost, and SVM -> saves best to models/asl_static_model.pkl
python src/train_Static.py
```

### Diagnostics & Demonstration Scripts:

```bash
# Plot confusion and error matrix heatmaps
python diagnostics/view_static_metrics.py
python diagnostics/view_static_metrics_error.py

# Run standalone OpenCV inference demos
python demos/demo_static_image.py <optional_path_to_image>
python demos/demo_static_video.py <optional_path_to_video>
python demos/demo_static_webcam.py
```

### 2. Dynamic Sign Transformer Pipeline

```bash
# Filter target vocabulary clips from raw data -> dataset/ASL_Dynamic
python src/setup_dynamic_dataset.py

# Extract sequence arrays -> data/ASL_Dynamic_Extracted
python src/video_preprocessing.py

# Inject synthetic neutral non-gesture frames
python src/create_neutral_class.py

# Apply Gaussian temporal noise & train/test split -> data/ASL_Dynamic_Augmented
python src/augment_data_dynamic.py

# Train Spatial-Temporal Transformer -> models/asl_dynamic_transformer.pth
python src/train_Transformer.py
```

### Diagnostics & Demonstration Scripts:

```bash
# Evaluate Transformer metrics & confusion matrices
python diagnostics/view_dynamic_metrics.py
python diagnostics/view_dynamic_metrics_error.py

# Run dynamic gesture demos
python demos/demo_dynamic_video.py <path_to_video>
python demos/demo_dynamic_webcam.py
```
## Web Application Deployment

To run the full-stack web interface, execute the FastAPI backend and React frontend concurrently in separate terminal windows.

### Step 1: Launch FastAPI Backend

```bash
cd web_app/backend
uvicorn app.main:app --reload --port 8000
```
- Interactive API documentation: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### Step 2: Launch React Frontend

```bash
# Open a new terminal tab
cd web_app
npm install
npm run dev
```
- Access the web interface at [http://localhost:5173](http://localhost:5173)

## Repository Structure

```
asl_translator/
├── dataset/                   # Raw & extracted dataset folders
├── data/                      # Processed landmark CSVs and .npy sequence files
├── diagnostics/               # Metric evaluation & plot generation tools
├── models/                    # Trained model weights & label encoders
│   ├── asl_rf_model.pkl
│   ├── asl_static_model.pkl
│   ├── static_label_encoder.pkl
│   ├── asl_dynamic_transformer.pth
│   ├── dynamic_label_encoder.pkl
│   └── hand_landmarker.task
├── src/                       # Core ML preprocessing and training modules
├── demos/                     # Standalone real-time OpenCV webcam demos
├── web_app/                   # Full-stack deployment suite
│   ├── backend/               # FastAPI REST microservice (app/main.py)
│   └── src/                   # React.js UI components & pages
├── requirements.txt           # Python package dependencies
└── README.md
```