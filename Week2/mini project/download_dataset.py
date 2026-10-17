"""
Plant Disease Dataset Downloader
Fetches a curated subset of high-quality leaf images from the official PlantVillage dataset.
"""

import os
import random
import json
import urllib.request
import urllib.parse
from concurrent.futures import ThreadPoolExecutor, as_completed

TARGET_CLASSES = [
    "Apple___healthy",
    "Apple___Black_rot",
    "Corn_(maize)___healthy",
    "Corn_(maize)___Common_rust_",
    "Pepper,_bell___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Potato___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Tomato___healthy",
    "Tomato___Early_blight",
    "Tomato___Late_blight"
]

IMAGES_PER_CLASS_TRAIN = 60
IMAGES_PER_CLASS_VAL = 15
SAMPLES_FOR_UI = 2

DATASET_DIR = os.path.join(os.path.dirname(__file__), "dataset")
SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "static", "samples")

def get_repo_tree():
    print("Fetching file manifest from GitHub...")
    url = "https://api.github.com/repos/spMohanty/PlantVillage-Dataset/git/trees/master?recursive=1"
    req = urllib.request.Request(url, headers={"User-Agent": "PlantDiseaseDetector/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.loads(resp.read().decode())
    
    class_files = {cls: [] for cls in TARGET_CLASSES}
    for item in data.get("tree", []):
        path = item.get("path", "")
        if path.startswith("raw/color/") and item.get("type") == "blob":
            parts = path.split("/")
            if len(parts) >= 3:
                cls_name = parts[2]
                if cls_name in class_files:
                    class_files[cls_name].append(path)
    
    return class_files

def download_single_file(repo_path, dest_path):
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    if os.path.exists(dest_path) and os.path.getsize(dest_path) > 1000:
        return True
    
    encoded_path = urllib.parse.quote(repo_path)
    url = f"https://raw.githubusercontent.com/spMohanty/PlantVillage-Dataset/master/{encoded_path}"
    
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=15) as resp, open(dest_path, "wb") as f:
                f.write(resp.read())
            return True
        except Exception as e:
            if attempt == 2:
                print(f"Failed to download {repo_path}: {e}")
                return False

def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    os.makedirs(SAMPLES_DIR, exist_ok=True)
    train_dir = os.path.join(DATASET_DIR, "train")
    val_dir = os.path.join(DATASET_DIR, "val")
    
    class_files = get_repo_tree()
    download_tasks = []
    
    sample_manifest = []

    print("\nPreparing download plan...")
    random.seed(42)
    for cls in TARGET_CLASSES:
        files = class_files.get(cls, [])
        if not files:
            print(f"Warning: No files found for {cls}")
            continue
        
        random.shuffle(files)
        total_needed = IMAGES_PER_CLASS_TRAIN + IMAGES_PER_CLASS_VAL + SAMPLES_FOR_UI
        selected = files[:total_needed]
        
        train_files = selected[:IMAGES_PER_CLASS_TRAIN]
        val_files = selected[IMAGES_PER_CLASS_TRAIN:IMAGES_PER_CLASS_TRAIN + IMAGES_PER_CLASS_VAL]
        sample_files = selected[IMAGES_PER_CLASS_TRAIN + IMAGES_PER_CLASS_VAL:total_needed]
        
        # Train downloads
        for idx, f in enumerate(train_files):
            ext = os.path.splitext(f)[1] or ".jpg"
            dest = os.path.join(train_dir, cls, f"img_{idx:03d}{ext}")
            download_tasks.append((f, dest))
            
        # Val downloads
        for idx, f in enumerate(val_files):
            ext = os.path.splitext(f)[1] or ".jpg"
            dest = os.path.join(val_dir, cls, f"val_{idx:03d}{ext}")
            download_tasks.append((f, dest))
            
        # Sample for UI
        for idx, f in enumerate(sample_files):
            ext = os.path.splitext(f)[1] or ".jpg"
            clean_cls = cls.replace("___", "_").replace(",", "").replace("(", "").replace(")", "").replace(" ", "_")
            sample_filename = f"{clean_cls}_sample_{idx+1}{ext}"
            dest = os.path.join(SAMPLES_DIR, sample_filename)
            download_tasks.append((f, dest))
            sample_manifest.append({
                "class_id": cls,
                "filename": sample_filename,
                "label": cls.replace("___", " - ").replace("_", " ").title()
            })

    # Save samples manifest
    with open(os.path.join(SAMPLES_DIR, "samples.json"), "w") as f:
        json.dump(sample_manifest, f, indent=2)

    total_tasks = len(download_tasks)
    print(f"Total images to download: {total_tasks} across {len(TARGET_CLASSES)} classes.")
    print("Downloading concurrently with 16 worker threads...")
    
    completed = 0
    with ThreadPoolExecutor(max_workers=16) as executor:
        futures = {executor.submit(download_single_file, t[0], t[1]): t for t in download_tasks}
        for future in as_completed(futures):
            res = future.result()
            completed += 1
            if completed % 50 == 0 or completed == total_tasks:
                print(f"Progress: {completed}/{total_tasks} ({completed * 100 // total_tasks}%)")

    print("\nDataset download completed successfully!")
    print(f"Train directory: {train_dir}")
    print(f"Validation directory: {val_dir}")
    print(f"Sample gallery directory: {SAMPLES_DIR}")

if __name__ == "__main__":
    main()
