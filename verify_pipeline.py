import sys
import os
import time

# Add project root to path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollVision.settings')

import django
django.setup()

from dashboard.face_utils import face_recognizer
import cv2
from django.conf import settings

def test_pipeline():
    print("Testing OpenCV SFace Pipeline...")
    
    face_recognizer.refresh_encodings()
    print(f"Model ID: {face_recognizer.detection_model}")
    print(f"Encodings Loaded: {len(face_recognizer.known_face_encodings)}")
    
    if face_recognizer.detector is None or face_recognizer.recognizer is None:
        print("❌ MODELS NOT LOADED!")
        return

    # Find test image
    faces_root = os.path.join(settings.MEDIA_ROOT, 'faces')
    test_image_path = None
    if os.path.exists(faces_root):
        for d in os.listdir(faces_root):
            path = os.path.join(faces_root, d)
            if os.path.isdir(path):
                files = [f for f in os.listdir(path) if f.endswith('.jpg')]
                if files:
                    test_image_path = os.path.join(path, files[0])
                    break
    
    if not test_image_path:
        print("No test image found.")
        return

    print(f"Testing image: {test_image_path}")
    image = cv2.imread(test_image_path)
    
    if image is None:
        print("❌ Failed to read image")
        return
        
    # 1. Detection
    t0 = time.time()
    faces = face_recognizer.detect_faces(image)
    print(f"Detection Time: {time.time()-t0:.3f}s")
    print(f"Faces Found: {len(faces)}")
    
    if not faces:
        print("❌ No faces detected!")
        return

    # 2. Encoding
    t0 = time.time()
    enc = face_recognizer.encode_face(image, faces[0])
    print(f"Encoding Time: {time.time()-t0:.3f}s")
    if enc:
        print(f"Vector Length: {len(enc['encoding'])}")
        print(f"Version: {enc.get('version')}")
        
    # 3. Recognition
    results = face_recognizer.recognize_faces(image)
    for res in results:
        print(f"Result: {res['student_id']} | Conf: {res['confidence']}% | Score: {res.get('score')} | Dist: {res.get('distance')}")
        if res['student_id']:
            print("✅ POSITIVE IDENTIFICATION")

if __name__ == "__main__":
    test_pipeline()
