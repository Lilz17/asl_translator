import os
import warnings
import pandas as pd
import numpy as np
import joblib
import time

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from xgboost import XGBClassifier
from sklearn.preprocessing import LabelEncoder

# Mute clutter
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# --- DYNAMIC PATHS ---
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUGMENTED_DATA_PATH = os.path.join(BASE_DIR, 'data', 'asl_landmarks_augmented.csv')

print("Loading augmented dataset...")
df = pd.read_csv(AUGMENTED_DATA_PATH)
X = df.drop(columns=['label'])
y = df['label']

# Encode text labels (A-Z) into numbers (0-23) for XGBoost compatibility
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

# Fixed 80/20 train/test split with stratification
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# --- DEFINE MODELS TO BENCHMARK ---
models = {
    "Random Forest": (
        RandomForestClassifier(n_estimators=100, random_state=42),
        os.path.join(BASE_DIR, 'archive', 'asl_rf_augmented.pkl')
    ),
    "SVM (RBF Kernel)": (
        SVC(kernel='rbf', C=10.0, gamma='scale', probability=True, random_state=42),
        os.path.join(BASE_DIR, 'archive', 'asl_svm_augmented.pkl')
    ),
    "XGBoost": (
        XGBClassifier(n_estimators=100, learning_rate=0.1, max_depth=6, random_state=42, eval_metric='mlogloss'),
        os.path.join(BASE_DIR, 'archive', 'asl_xgboost_augmented.pkl')
    )
}

results = []
best_acc = 0.0
winning_model_name = ""
winning_model_obj = None

print("\nStarting Model Comparison Benchmark...")
print("=" * 68)

for name, (model, save_path) in models.items():
    start_time = time.time()
    
    # Train
    model.fit(X_train, y_train)
    train_time = time.time() - start_time
    
    # Inference Latency Benchmark
    start_inf = time.time()
    y_pred = model.predict(X_test)
    inf_time = (time.time() - start_inf) / len(X_test) * 1000  # ms per sample
    
    # Evaluate
    acc = accuracy_score(y_test, y_pred)
    
    # Save individual model weights
    joblib.dump(model, save_path)
    
    results.append({
        "Model": name,
        "Accuracy": f"{acc * 100:.2f}%",
        "Train Time (s)": f"{train_time:.2f}s",
        "Latency / Sample": f"{inf_time:.3f} ms"
    })
    
    # Track overall winner
    if acc > best_acc:
        best_acc = acc
        winning_model_name = name
        winning_model_obj = model

print("\n" + "=" * 68)
print("BENCHMARK RESULTS SUMMARY")
print("=" * 68)
summary_df = pd.DataFrame(results)
print(summary_df.to_string(index=False))
print("=" * 68)

# Save the absolute winner to a separate dedicated file
BEST_MODEL_PATH = os.path.join(BASE_DIR, 'models', 'asl_static_model.pkl')
joblib.dump(winning_model_obj, BEST_MODEL_PATH)
joblib.dump(label_encoder, os.path.join(BASE_DIR, 'models', 'static_label_encoder.pkl'))

print(f"\nWinner: {winning_model_name} with {best_acc * 100:.2f}% accuracy!")
print(f"Saved winning model separately to: {BEST_MODEL_PATH}")