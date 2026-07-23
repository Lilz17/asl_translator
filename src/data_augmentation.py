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

OLD_DATA_PATH = 'data/asl_landmarks.csv'
NEW_DATA_PATH = 'data/asl_landmarks_augmented.csv'
BASELINE_MODEL_PATH = 'models/asl_rf_model.pkl'

# --- AUTOMATION STEP: Identify Problem Classes From Metrics ---
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

# Automatically flags any class where the F1-score or recall is below 95%
ACCURACY_THRESHOLD = 0.95
DYNAMIC_PROBLEM_CLASSES = []

for key, metrics in report.items():
    # Only evaluate individual alphabet labels, skipping global summary keys
    if key in y_orig.unique() and metrics['recall'] < ACCURACY_THRESHOLD:
        DYNAMIC_PROBLEM_CLASSES.append(key)

print(f"Metric-Driven Analysis Complete.")
print(f"Classes automatically targeted for augmentation (Recall < {ACCURACY_THRESHOLD*100}%): {sorted(DYNAMIC_PROBLEM_CLASSES)}")
# -------------------------------------------------------------

print("\nRunning geometric augmentation pipeline...")
original_rows = len(df_orig)
augmented_records = []

for idx, row in df_orig.iterrows():
    label = row['label']
    coords = row.drop('label').values.astype(float)
    
    # KEEP ORIGINAL ROW UNTOUCHED
    augmented_records.append(row.values)
    
    # If it was dynamically flagged as a weak spot, generate 3 mutated copies
    if label in DYNAMIC_PROBLEM_CLASSES:
        for _ in range(3):
            # 1. Apply Jitter Noise
            noise = np.random.normal(0, 0.0015, size=coords.shape)
            jittered_coords = coords + noise
            
            # 2. Apply Subtle 2D Rotation Matrix (Wrist Tilt)
            theta = np.radians(np.random.uniform(-8, 8))
            cos_t, sin_t = np.cos(theta), np.sin(theta)
            
            rotated_coords = jittered_coords.copy()
            for j in range(21):
                x_idx, y_idx = j * 3, j * 3 + 1
                x, y = rotated_coords[x_idx], rotated_coords[y_idx]
                rotated_coords[x_idx] = x * cos_t - y * sin_t
                rotated_coords[y_idx] = x * sin_t + y * cos_t
            
            new_row = np.insert(rotated_coords.astype(object), 0, label)
            augmented_records.append(new_row)

# Rebuild and shuffle
columns = ['label'] + [f'{axis}{i}' for i in range(21) for axis in ['x', 'y', 'z']]
augmented_df = pd.DataFrame(augmented_records, columns=columns)
augmented_df = augmented_df.sample(frac=1, random_state=42).reset_index(drop=True)

augmented_df.to_csv(NEW_DATA_PATH, index=False)
print(f"\nAugmentation Complete!")
print(f"Original Rows: {original_rows} -> Total Augmented Dataset Rows: {len(augmented_df)}")