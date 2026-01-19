import cv2
import numpy as np
import face_recognition

print("Testing face_encodings isolation...")

# Create a dummy image (100x100 RGB)
img = np.zeros((100, 100, 3), dtype=np.uint8)
img = np.ascontiguousarray(img)

# Define a dummy face location (top, right, bottom, left)
# The image is black so encoding will be garbage, but we just want to see if it CRASHES.
known_location = [(10, 90, 90, 10)]

try:
    print("Attempting to encode face with known location...")
    encodings = face_recognition.face_encodings(img, known_location)
    print("✅ SUCCESS: Encoding function works!")
except Exception as e:
    print(f"❌ FAILED: Encoding function crashed: {e}")

print("Test complete.")
