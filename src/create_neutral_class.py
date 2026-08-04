import numpy as np
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "ASL_Dynamic_Extracted" / "neutral"

NUM_SAMPLES = 300
SEQUENCE_LENGTH = 30
FEATURE_DIM = 66  # Updated to 66


def generate_still_hand():
    base_pose = np.random.normal(0, 0.05, (20, 3))  # 20 finger landmarks
    wrist_pos = np.array([0.5, 0.5, 0.0])          # Center frame wrist
    
    sequence = []
    for _ in range(SEQUENCE_LENGTH):
        finger_jitter = (base_pose + np.random.normal(0, 0.003, (20, 3))).flatten()
        wrist_jitter = wrist_pos + np.random.normal(0, 0.001, 3)
        velocity = np.random.normal(0, 0.0005, 3)
        
        frame = np.hstack([finger_jitter, wrist_jitter, velocity])
        sequence.append(frame)
        
    return np.array(sequence)


def generate_wandering_hand():
    base_pose = np.random.normal(0, 0.05, (20, 3))
    wrist_pos = np.array([0.5, 0.5, 0.0])
    
    sequence = []
    drift = np.random.normal(0, 0.005, 3)
    
    for _ in range(SEQUENCE_LENGTH):
        wrist_pos += drift
        finger_jitter = (base_pose + np.random.normal(0, 0.003, (20, 3))).flatten()
        frame = np.hstack([finger_jitter, wrist_pos, drift])
        sequence.append(frame)
        
    return np.array(sequence)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Generating {NUM_SAMPLES} synthetic 66-dim 'Neutral' sequences...")

    for i in range(NUM_SAMPLES):
        seq = generate_still_hand() if i % 2 == 0 else generate_wandering_hand()
        np.save(OUTPUT_DIR / f"neutral_{i+1:03d}.npy", seq)

    print(f"Created Neutral sequences under '{OUTPUT_DIR.resolve()}'")


if __name__ == "__main__":
    main()