import os
import shutil
import numpy as np
from pathlib import Path
from sklearn.model_selection import train_test_split

PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_EXTRACTED_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Extracted"
OUTPUT_AUG_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Augmented"

AUGMENT_FACTOR = 4  # Generates 4 augmented copies per training sample
FEATURE_DIM = 66    # 60 finger features + 3 wrist coords + 3 velocity terms


def apply_random_rotation(aug_seq, max_angle_deg=10):
    """Rotates the 20 finger landmarks around the origin."""
    angle_rad = np.radians(np.random.uniform(-max_angle_deg, max_angle_deg))
    cos_a, sin_a = np.cos(angle_rad), np.sin(angle_rad)

    # 2D Rotation Matrix around Z-axis
    rot_matrix = np.array([
        [cos_a, -sin_a, 0],
        [sin_a,  cos_a, 0],
        [    0,      0, 1]
    ])

    rotated_seq = np.zeros_like(aug_seq)
    for t in range(len(aug_seq)):
        # Reshape only finger landmarks (60 values -> 20 x 3)
        finger_lms = aug_seq[t, :60].reshape(20, 3)
        rotated_fingers = np.dot(finger_lms, rot_matrix.T)
        
        # Keep spatial wrist coordinates & velocity intact
        spatial_features = aug_seq[t, 60:]
        
        rotated_seq[t] = np.hstack([rotated_fingers.flatten(), spatial_features])

    return rotated_seq


def apply_gaussian_jitter(aug_seq, noise_std=0.005):
    """Adds small Gaussian noise to finger coordinates and spatial features."""
    noise = np.random.normal(0, noise_std, aug_seq.shape)
    return aug_seq + noise


def augment_sequence(base_seq):
    aug = base_seq.copy()
    aug = apply_random_rotation(aug)
    aug = apply_gaussian_jitter(aug)
    return aug


def main():
    if not RAW_EXTRACTED_DIR.exists():
        raise FileNotFoundError(f"Cannot find raw features directory at {RAW_EXTRACTED_DIR}")

    # Prepare Train / Val directory structures
    train_dir = OUTPUT_AUG_DIR / "train"
    val_dir = OUTPUT_AUG_DIR / "val"

    if OUTPUT_AUG_DIR.exists():
        shutil.rmtree(OUTPUT_AUG_DIR)

    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)

    class_folders = [f for f in RAW_EXTRACTED_DIR.iterdir() if f.is_dir()]
    print(f"Splitting and augmenting 66-dim data across {len(class_folders)} classes...\n")

    for class_folder in class_folders:
        class_name = class_folder.name
        npy_files = list(class_folder.glob("*.npy"))

        if len(npy_files) < 2:
            print(f"Skipping class '{class_name}' - insufficient samples.")
            continue

        train_files, val_files = train_test_split(
            npy_files, test_size=0.20, random_state=42, shuffle=True
        )

        train_class_dir = train_dir / class_name
        val_class_dir = val_dir / class_name
        train_class_dir.mkdir(parents=True, exist_ok=True)
        val_class_dir.mkdir(parents=True, exist_ok=True)

        # Save Validation Set (Originals only, unaugmented)
        for val_file in val_files:
            shutil.copy(val_file, val_class_dir / val_file.name)

        # Save Training Set + Augmentations
        for train_file in train_files:
            base_seq = np.load(train_file)
            shutil.copy(train_file, train_class_dir / train_file.name)

            for aug_idx in range(AUGMENT_FACTOR):
                aug_seq = augment_sequence(base_seq)
                aug_filename = f"{train_file.stem}_aug{aug_idx+1}.npy"
                np.save(train_class_dir / aug_filename, aug_seq)

        print(f"✓ Class '{class_name}': {len(train_files) * (AUGMENT_FACTOR + 1)} train samples, {len(val_files)} val samples.")

    print("\nData augmentation complete! Prepped data ready in 'data/ASL_Dynamic_Augmented'.")


if __name__ == "__main__":
    main()