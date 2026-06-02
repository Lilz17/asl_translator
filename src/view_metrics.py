import os
import warnings
import pandas as pd
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import numpy as np

warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

DATA_PATH = 'data/asl_landmarks.csv'
MODEL_PATH = 'models/asl_rf_model.pkl'

print("Loading dataset and pre-trained weights...")
df = pd.read_csv(DATA_PATH)
X = df.drop(columns=['label'])
y = df['label']

# Replicate the exact same split used during training
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

# Load the saved model and make predictions on the test set
model = joblib.load(MODEL_PATH)
y_pred = model.predict(X_test)

# Display Metrics
print("\n================ CLASSIFICATION REPORT ================")
print(classification_report(y_test, y_pred))

# Visualize Confusion Matrix
print("Generating visual Confusion Matrix heatmap...")
labels = sorted(y.unique())
#cm = confusion_matrix(y_test, y_pred, labels=labels)
cm_absolute = confusion_matrix(y_test, y_pred, labels=labels) # absolute counts
cm_normalized = cm_absolute.astype('float') / cm_absolute.sum(axis=1)[:, np.newaxis] # normalize by row

plt.figure(figsize=(14, 10))

#sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
#             xticklabels=labels, yticklabels=labels)

# colours will be determined by the normalized values to show relative performance, but annotated with absolute counts for clarity
sns.heatmap(cm_normalized, annot=cm_absolute, fmt='d', cmap='Blues', 
          xticklabels=labels, yticklabels=labels, vmin=0, vmax=1)

plt.title('ASL Sign Recognition - Confusion Matrix Heatmap', fontsize=16)
plt.xlabel('Predicted Alphabet Sign', fontsize=12)
plt.ylabel('Actual Alphabet Sign', fontsize=12)
plt.tight_layout()

print("Opening visual window... Close the window pane to exit.")
plt.show()