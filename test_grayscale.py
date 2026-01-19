import cv2
import numpy as np
import face_recognition

print("Testing GRAYSCALE isolation...")

# Create a Grayscale image (100x100 2D)
img_gray = np.zeros((100, 100), dtype=np.uint8)
img_gray = np.ascontiguousarray(img_gray)

print(f"Shape: {img_gray.shape},  Dtype: {img_gray.dtype}, Contiguous: {img_gray.flags['C_CONTIGUOUS']}")

try:
    print("Testing face_locations (Detection) on Grayscale...")
    faces = face_recognition.face_locations(img_gray)
    print("✅ SUCCESS: Detection works on Grayscale!")
except Exception as e:
    print(f"❌ FAILED Detection: {e}")

try:
    print("Testing face_encodings (Recognition) on Grayscale...")
    # Dummy location
    faces = [(10, 90, 90, 10)]
    encodings = face_recognition.face_encodings(img_gray, faces)
    print("✅ SUCCESS: Encoding works on Grayscale!")
except Exception as e:
    print(f"❌ FAILED Encoding: {e}")

print("Test complete.")
