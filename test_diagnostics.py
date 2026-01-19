import cv2
import numpy as np
import face_recognition
import sys

print(f"Python: {sys.version}")
try:
    import dlib
    print(f"Dlib: {dlib.__version__}")
except:
    print("Dlib: Unknown")

def test_format(name, img_array):
    print(f"\n--- Testing {name} ---")
    print(f"Shape: {img_array.shape}, Dtype: {img_array.dtype}")
    print(f"Contiguous: {img_array.flags['C_CONTIGUOUS']}")
    
    try:
        faces = face_recognition.face_locations(img_array)
        print(f"✅ SUCCESS")
        return True
    except Exception as e:
        print(f"❌ FAILED: {str(e)}")
        return False

# 1. Standard RGB
img_rgb = np.zeros((100, 100, 3), dtype=np.uint8)
test_format("RGB uint8 (3-channel)", img_rgb)

# 2. Grayscale
img_gray = np.zeros((100, 100), dtype=np.uint8)
test_format("Grayscale uint8 (2-channel)", img_gray)

# 3. Contiguous RGB
img_contig = np.ascontiguousarray(img_rgb)
test_format("Contiguous RGB", img_contig)

# 4. Larger image
img_large = np.zeros((500, 500, 3), dtype=np.uint8)
test_format("Large RGB", img_large)
