import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set up visual aesthetics
plt.style.use('ggplot')
sns.set_palette('muted')

# Resolve project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = PROJECT_ROOT / "data" / "asl_landmarks.csv"

def perform_eda():
    if not DATA_PATH.exists():
        print(f"❌ Error: {DATA_PATH} not found. Please run image_preprocessing.py first.")
        return

    print("==================================================")
    print("📊 EXPLORATORY DATA ANALYSIS (ASL STATIC LANDMARKS)")
    print("==================================================\n")

    # Load Dataset
    df = pd.read_csv(DATA_PATH)
    
    # 1. Dataset Shape & Missing Values
    print(f"• Dataset Dimensions: {df.shape[0]} rows (samples) × {df.shape[1]} columns")
    print(f"• Total Features: {df.shape[1] - 1} coordinate dimensions (x0..z20)")
    print(f"• Missing/Null Values: {df.isnull().sum().sum()}")
    
    # Identify target column (usually 'label' or 'target')
    target_col = 'label' if 'label' in df.columns else df.columns[-1]
    
    # 2. Class Distribution Analysis
    class_counts = df[target_col].value_counts().sort_index()
    total_samples = len(df)
    
    print(f"\n• Unique Classes ({len(class_counts)} Total):")
    print("--------------------------------------------------")
    for cls, count in class_counts.items():
        percentage = (count / total_samples) * 100
        print(f"  Class '{cls}': {count} samples ({percentage:.2f}%)")
        
    imbalance_ratio = class_counts.max() / class_counts.min()
    print(f"\n• Class Imbalance Ratio (Max / Min): {imbalance_ratio:.2f}x")
    
    # 3. Coordinate Feature Distribution Summary
    feature_cols = [col for col in df.columns if col != target_col]
    X = df[feature_cols]
    
    print("\n• Relative Coordinate Ranges (Wrist Anchor Normalized):")
    print(f"  Min Value: {X.values.min():.4f}")
    print(f"  Max Value: {X.values.max():.4f}")
    print(f"  Mean Value: {X.values.mean():.4f}")
    print(f"  Std Dev:    {X.values.std():.4f}")

    # --------------------------------------------------
    # PLOTTING EDA CHARTS
    # --------------------------------------------------
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Chart 1: Class Distribution Bar Plot
    sns.barplot(x=class_counts.index, y=class_counts.values, ax=axes[0], palette="viridis")
    axes[0].set_title("1. Class Distribution Across Static Alphabet Signs", fontsize=12, fontweight='bold')
    axes[0].set_xlabel("Sign Class")
    axes[0].set_ylabel("Number of Samples")
    axes[0].tick_params(axis='x', rotation=45)

    # Chart 2: Coordinate Spread Distribution (Histogram)
    sns.histplot(X.values.flatten(), bins=50, kde=True, ax=axes[1], color="teal")
    axes[1].set_title("2. Wrist-Relative Coordinate Feature Distribution", fontsize=12, fontweight='bold')
    axes[1].set_xlabel("Normalized Coordinate Value (Relative to Wrist lm_0)")
    axes[1].set_ylabel("Frequency Density")

    plt.tight_layout()
    
    # Save EDA Plot
    output_plot = PROJECT_ROOT / "diagnostics" / "eda_summary_plot.png"
    plt.savefig(output_plot, dpi=300)
    print(f"\n✓ EDA Summary Plots successfully saved to: {output_plot}")
    plt.show()

if __name__ == "__main__":
    perform_eda()