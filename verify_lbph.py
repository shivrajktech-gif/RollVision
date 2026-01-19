import cv2
import sys

print(f"OpenCV Version: {cv2.__version__}")
try:
    # Try creating the recognizer
    if hasattr(cv2, 'face'):
        rec = cv2.face.LBPHFaceRecognizer_create()
        print("✅ LBPH Available (cv2.face found)")
    else:
        print("❌ cv2.face missing - opencv-contrib-python not installed correctly")
except Exception as e:
    print(f"❌ Error checking LBPH: {e}")
