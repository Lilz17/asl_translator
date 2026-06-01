# Training a Random Model Classifier on the static signs coordinates saved in the asl_landmarks.csv file

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib

# joblib is used to save the trained model weights to disk for future use.

# 1. Load the generated dataset
DATA_PATH = 'asl_landmarks.csv'
print(f"Loading dataset from {DATA_PATH}...")
df = pd.read_csv(DATA_PATH)

# Separate features (X) from labels (y)
# X takes all columns except the 'label' column
X = df.drop(columns=['label'])
y = df['label']

print(f"Dataset loaded. Total samples: {len(df)}, Total features per sample: {X.shape[1]}")

# 2. Split into Training (80%) and Testing (20%) sets
# stratify=y ensures balanced distribution of letters in both splits
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# 3. Initialize and train the Random Forest Classifier
print("Training Random Forest Classifier...")
model = RandomForestClassifier(n_estimators=100, random_state=42, n_jobs=-1) 
# n_jobs=-1 tells the CPU to use all available cores for maximum speed

model.fit(X_train, y_train)
print("Model training completed.")

# 4. Evaluate performance
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)

print("\n================ MODEL EVALUATION ================")
print(f"Overall Accuracy: {accuracy * 100:.2f}%")
print("\nClassification Report:")
print(classification_report(y_test, y_pred))

# 5. Save the trained model weights to disk
# .pkl files are added to your .gitignore so this stays local
MODEL_OUTPUT = 'asl_rf_model.pkl'
joblib.dump(model, MODEL_OUTPUT)
print(f"Model saved successfully to {MODEL_OUTPUT}")