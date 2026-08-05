import os
import json
import shutil
from pathlib import Path

# ==========================================
# Path & Word Definitions
# ==========================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent
BASE_DIR = PROJECT_ROOT / "dataset"

# Input Paths
SIGNN_DIR = BASE_DIR / "ASL_J_Z" / "SigNN Video Data"
WLASL_VIDEOS_DIR = BASE_DIR / "ASL_Dynamic_FULL" / "WLASL-complete-curated" / "videos"
WLASL_JSON_PATH = BASE_DIR / "ASL_Dynamic_FULL" / "WLASL-complete-curated" / "WLASL_custom_split.json"

# Target Output Directory
OUTPUT_DIR = BASE_DIR / "ASL_Dynamic"

# Word Mapping: Target folder name -> WLASL Gloss name(s)
# Handles multi-word gloss variations (e.g. "thank you" in WLASL is usually "thankyou")
TARGET_WORDS = {
    "hello": ["hello"],
    "goodbye": ["goodbye", "bye"],
    "please": ["please"],
    "help": ["help"],
    "sorry": ["sorry"],
    "yes": ["yes"],
    "no": ["no"],
    "thank_you": ["thankyou", "thank you"],
    "my": ["my"],
    "name": ["name"]
}

# ==========================================
# Copy SigNN J & Z
# ==========================================
def copy_signn_letters():
    print("Processing SigNN J and Z datasets...")
    for letter in ["J", "Z"]:
        src_folder = SIGNN_DIR / letter
        dst_folder = OUTPUT_DIR / letter
        dst_folder.mkdir(parents=True, exist_ok=True)

        if not src_folder.exists():
            print(f"Warning: SigNN folder for '{letter}' not found at {src_folder}")
            continue

        video_files = list(src_folder.glob("*.avi")) + list(src_folder.glob("*.mp4"))
        copied_count = 0
        for vid in video_files:
            shutil.copy2(vid, dst_folder / vid.name)
            copied_count += 1

        print(f"  ✓ [{letter}] Copied {copied_count} files into {dst_folder}")

# ==========================================
# Extract Chosen Words from WLASL
# ==========================================
def extract_wlasl_words():
    print("\nExtracting selected target words from WLASL...")
    
    if not WLASL_JSON_PATH.exists():
        print(f"Error: WLASL JSON file not found at {WLASL_JSON_PATH}")
        return

    with open(WLASL_JSON_PATH, "r", encoding="utf-8") as f:
        wlasl_data = json.load(f)

    # Invert mapping to fast-lookup dictionary: WLASL_gloss -> Target_folder_name
    gloss_to_folder = {}
    for folder_name, gloss_list in TARGET_WORDS.items():
        for gloss in gloss_list:
            gloss_to_folder[gloss.lower()] = folder_name

    stats = {folder: 0 for folder in TARGET_WORDS.keys()}

    for item in wlasl_data:
        gloss = item.get("gloss", "").lower()
        
        if gloss in gloss_to_folder:
            folder_name = gloss_to_folder[gloss]
            dst_folder = OUTPUT_DIR / folder_name
            dst_folder.mkdir(parents=True, exist_ok=True)

            for instance in item.get("instances", []):
                video_id = instance.get("video_id")
                
                # Check for possible video extensions
                mp4_src = WLASL_VIDEOS_DIR / f"{video_id}.mp4"
                
                if mp4_src.exists():
                    dst_path = dst_folder / f"wlasl_{video_id}.mp4"
                    shutil.copy2(mp4_src, dst_path)
                    stats[folder_name] += 1

    for word, count in stats.items():
        print(f"  ✓ [{word}] Extracted {count} videos into {OUTPUT_DIR / word}")

# ==========================================
# Main Execution Flow
# ==========================================
if __name__ == "__main__":
    print("==============================================")
    print("   ASL Dynamic Dataset Filter & Assembler     ")
    print("==============================================\n")
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    copy_signn_letters()
    extract_wlasl_words()
    
    print("\nSuccess! Your dynamic dataset is prepared in:")
    print(f"   {OUTPUT_DIR.resolve()}")