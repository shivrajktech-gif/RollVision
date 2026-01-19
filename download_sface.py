import urllib.request
import os

MODELS_DIR = r"c:\Users\aades\OneDrive\Desktop\DJANGO - Copy\folder\project\RollVision\dashboard\models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Delete the text file to force re-download
path = os.path.join(MODELS_DIR, "face_recognition_sface_2021dec.onnx")
if os.path.exists(path) and os.path.getsize(path) < 1000:
    print("Deleting invalid LFS pointer file...")
    os.remove(path)

files = {
    # Using blob/.../?raw=true often resolves LFS better than raw.githubusercontent
    "face_recognition_sface_2021dec.onnx": "https://github.com/opencv/opencv_zoo/blob/main/models/face_recognition_sface/face_recognition_sface_2021dec.onnx?raw=true"
}

print(f"Downloading models to {MODELS_DIR}...")

for name, url in files.items():
    path = os.path.join(MODELS_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 1000:
        print(f"Skipping {name} (already exists and looks valid)")
        continue
        
    print(f"Downloading {name}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"✅ Downloaded {name}")
        size = os.path.getsize(path)
        print(f"Size: {size} bytes")
        if size < 1000:
            print("⚠️ WARNING: File is too small, likely still an LFS pointer!")
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

print("Done.")
