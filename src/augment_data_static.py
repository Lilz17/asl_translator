import os
import warnings
import pandas as pd
import numpy as np
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Mute clutter
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# project root folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

OLD_DATA_PATH = os.path.join(BASE_DIR, 'data', 'asl_landmarks.csv')
NEW_DATA_PATH = os.path.join(BASE_DIR, 'data', 'asl_landmarks_augmented.csv')
BASELINE_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'asl_rf_model.pkl')

# Set explicit seed for reproducible data generation
np.random.seed(42)

# --- AUTOMATION STEP: Identify Weak Classes From Baseline Metrics ---
print("Evaluating baseline model to detect performance weak spots...")
df_orig = pd.read_csv(OLD_DATA_PATH)
X_orig = df_orig.drop(columns=['label'])
y_orig = df_orig['label']

# Replicate the exact standard baseline validation split
_, X_test, _, y_test = train_test_split(
    X_orig, y_orig, test_size=0.2, random_state=42, stratify=y_orig
)

# Load baseline and get the per-class report dictionary
baseline_model = joblib.load(BASELINE_MODEL_PATH)
y_pred = baseline_model.predict(X_test)
report = classification_report(y_test, y_pred, output_dict=True)

# Automatically flags any class where recall is below 95%
ACCURACY_THRESHOLD = 0.95
DYNAMIC_PROBLEM_CLASSES = []

for key, metrics in report.items():
    if key in y_orig.unique() and metrics['recall'] < ACCURACY_THRESHOLD:
        DYNAMIC_PROBLEM_CLASSES.append(key)

print("Metric-Driven Analysis Complete.")
print(f"Weak Classes (Recall < {ACCURACY_THRESHOLD*100}%): {sorted(DYNAMIC_PROBLEM_CLASSES)}")
# -------------------------------------------------------------

print("\nRunning geometric rotation & jitter augmentation pipeline...")
original_rows = len(df_orig)
augmented_records = []

for idx, row in df_orig.iterrows():
    label = row['label']
    coords = row.drop('label').values.astype(float)
    
    # Keep the untouched original sample
    augmented_records.append(row.values)
    
    # General Rotation Augmentation
    # Adding a small rotation to all classes to account for real world hand signs being slightly rotated
    # Generate 1 rotated copy with broader tilt range (-25 to +25 degrees)
    theta_gen = np.radians(np.random.uniform(-25, 25))
    cos_g, sin_g = np.cos(theta_gen), np.sin(theta_gen)
    gen_rotated = coords.copy()
    
    for j in range(21):
        x_idx, y_idx = j * 3, j * 3 + 1
        x, y = gen_rotated[x_idx], gen_rotated[y_idx]
        gen_rotated[x_idx] = x * cos_g - y * sin_g
        gen_rotated[y_idx] = x * sin_g + y * cos_g
        
    augmented_records.append(np.insert(gen_rotated.astype(object), 0, label))

    # Targeted Heavy Augmentation for Dynamically Flagged Weak Spots (Fist Signs)
    if label in DYNAMIC_PROBLEM_CLASSES:
        for _ in range(2):
            # Apply Gaussian Jitter + Rotation Matrix
            noise = np.random.normal(0, 0.0015, size=coords.shape)
            jittered_coords = coords + noise
            
            theta_weak = np.radians(np.random.uniform(-15, 15))
            cos_w, sin_w = np.cos(theta_weak), np.sin(theta_weak)
            
            weak_rotated = jittered_coords.copy()
            for j in range(21):
                x_idx, y_idx = j * 3, j * 3 + 1
                x, y = weak_rotated[x_idx], weak_rotated[y_idx]
                weak_rotated[x_idx] = x * cos_w - y * sin_w
                weak_rotated[y_idx] = x * sin_w + y * cos_w
            
            augmented_records.append(np.insert(weak_rotated.astype(object), 0, label))

# Rebuild and shuffle
columns = ['label'] + [f'{axis}{i}' for i in range(21) for axis in ['x', 'y', 'z']]
augmented_df = pd.DataFrame(augmented_records, columns=columns)
augmented_df = augmented_df.sample(frac=1, random_state=42).reset_index(drop=True)

# Ensure data directory exists
os.makedirs(os.path.dirname(NEW_DATA_PATH), exist_ok=True)
augmented_df.to_csv(NEW_DATA_PATH, index=False)

print("\nAugmentation Complete!")
print(f"Original Dataset Size: {original_rows} rows")
print(f"Augmented Dataset Size: {len(augmented_df)} rows")
print(f"Saved to: {NEW_DATA_PATH}")