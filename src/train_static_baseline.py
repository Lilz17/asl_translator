# Training a Random Model Classifier on the static signs coordinates saved in the asl_landmarks.csv file

import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path

# joblib is used to save the trained model weights to disk for future use.

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / 'data' / 'asl_landmarks.csv'
MODEL_SAVE_PATH = PROJECT_ROOT / 'models' / 'asl_rf_model.pkl'
MODEL_SAVE_PATH.parent.mkdir(parents=True, exist_ok=True) # verifying the folder exists

# Load the generated dataset
print(f"Loading dataset from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Separate features (X) from labels (y)
# X takes all columns except the 'label' column
X = df.drop(columns=['label'])
y = df['label']

print(f"Dataset loaded. Total samples: {len(df)}, Total features per sample: {X.shape[1]}")

# Split into Training (80%) and Testing (20%) sets
# stratify=y ensures balanced distribution of letters in both splits
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Initialize and train the Random Forest Classifier
print("Training Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1) 
# n_jobs=-1 tells the CPU to use all available cores for maximum speed

model.fit(X_train, y_train)
print("Model training completed.")

# Evaluate performance
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n================ MODEL EVALUATION ================")
print(f"Overall Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# Save the trained model weights to disk
joblib.dump(model, MODEL_SAVE_PATH)
print(f"Model saved successfully to {MODEL_SAVE_PATH}")