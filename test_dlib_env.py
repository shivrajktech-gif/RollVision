import cv2
import numpy as np
import face_recognition
import sys

print(f"Python: {sys.version}")
print(f"Numpy: {np.__version__}")
try:
    import dlib
    print(f"Dlib: {dlib.__version__}")
except ImportError:
    print("Dlib: Not directly importable or missing")

print(f"Face Recognition: {face_recognition.__dict__.get('__version__', 'unknown')}")

# Create a valid 8-bit RGB image (black square)
img = np.zeros((100, 100, 3), dtype=np.uint8)
print(f"\nTest Image Stats:")
print(f"Shape: {img.shape}")
print(f"Dtype: {img.dtype}")
print(f"Contiguous: {img.flags['C_CONTIGUOUS']}")

try:
    print("\nAttempting face detection on synthetic image...")
    # This should return empty list, not crash
    faces = face_recognition.face_locations(img)
    print("✅ Success! face_recognition is working.")
    print(f"Found faces: {len(faces)}")
except Exception as e:
    print(f"❌ CRITICAL FAILURE: {e}")

print("\nSystem check complete.")
