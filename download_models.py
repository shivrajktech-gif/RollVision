import urllib.request
import os

MODELS_DIR = r"c:\Users\aades\OneDrive\Desktop\DJANGO - Copy\folder\project\RollVision\dashboard\models"
os.makedirs(MODELS_DIR, exist_ok=True)

files = {
    "deploy.prototxt": "https://raw.githubusercontent.com/opencv/opencv/master/samples/dnn/face_detector/deploy.prototxt",
    "res10_300x300_ssd_iter_140000.caffemodel": "https://raw.githubusercontent.com/opencv/opencv_3rdparty/dnn_samples_face_detector_20170830/res10_300x300_ssd_iter_140000.caffemodel",
    "openface_nn4.small2.v1.t7": "https://github.com/pyannote/pyannote-data/raw/master/openface.nn4.small2.v1.t7"
}

print(f"Downloading models to {MODELS_DIR}...")

for name, url in files.items():
    path = os.path.join(MODELS_DIR, name)
    if os.path.exists(path) and os.path.getsize(path) > 0:
        print(f"Skipping {name} (already exists)")
        continue
        
    print(f"Downloading {name}...")
    try:
        urllib.request.urlretrieve(url, path)
        print(f"✅ Downloaded {name}")
    except Exception as e:
        print(f"❌ Failed to download {name}: {e}")

print("Done.")
