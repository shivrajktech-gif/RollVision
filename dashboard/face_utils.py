"""
Face Detection and Recognition Utilities for RollVision Attendance System
Uses OpenCV DNN SFace (State-of-the-Art) for high accuracy.
"""

import cv2
import numpy as np
import os
import json
import base64
import secrets
import time
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

# ==================== Configuration ====================
# SFace uses Cosine Similarity (not Distance).
# Threshold recommended is 0.363.
FACE_MATCH_THRESHOLD = 0.4  # Matches > 0.4 score
FACE_DETECTION_THRESHOLD = 0.15   # SSD confidence (VERY LOW for debugging)
FACE_MIN_SIZE = (80, 80)
ENABLE_PREPROCESSING = True
ENABLE_QUALITY_CHECKS = True

class FaceDetectionError(Exception):
    """Custom exception for face detection errors"""
    pass

class FaceRecognizer:
    """Handle face detection and SFace recognition"""
    
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_ids = []
        self._is_trained = False
        self.detection_model = "opencv_sface_2021"
        
        # Paths
        models_dir = os.path.join(settings.BASE_DIR, 'dashboard', 'models')
        
        # Detection Model (ResNet SSD) - KEEPING THIS AS IT WORKS WELL
        self.proto_path = os.path.join(models_dir, 'deploy.prototxt')
        self.model_path = os.path.join(models_dir, 'res10_300x300_ssd_iter_140000.caffemodel')
        
        # Recognition Model (SFace)
        self.sface_path = os.path.join(models_dir, 'face_recognition_sface_2021dec.onnx')
        
        # Load Networks
        try:
            self.detector = cv2.dnn.readNetFromCaffe(self.proto_path, self.model_path)
            self.recognizer = cv2.dnn.readNetFromONNX(self.sface_path)
            logger.info("OpenCV SFace Models loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load DNN models: {e}")
            self.detector = None
            self.recognizer = None
            
        # Initialize Cache
        self.refresh_encodings()

    def refresh_encodings(self):
        """Load all valid encodings from DB into memory"""
        try:
            from dashboard.models import FaceEncoding
            
            encodings = FaceEncoding.objects.filter(is_active=True).select_related('student')
            
            self.known_face_encodings = []
            self.known_face_ids = []
            
            count = 0
            for enc in encodings:
                try:
                    data = json.loads(enc.encoding_data)
                    # Handle version differences
                    if isinstance(data, dict):
                        if data.get('version') == 'opencv_sface_v1':
                            vec = np.array(data['encoding'])
                            self.known_face_encodings.append(vec)
                            self.known_face_ids.append(enc.student.student_id)
                            count += 1
                    # Old versions skipped (must retrain)
                except Exception as e:
                    logger.error(f"Failed to load encoding for {enc.student.student_id}: {e}")
            
            self._is_trained = (count > 0)
            logger.info(f"Loaded {count} SFace encodings into memory.")
            return True
            
        except Exception as e:
            logger.error(f"Error refreshing encodings: {e}")
            return False

    def detect_faces(self, image, preprocess=True):
        """
        Detect faces using OpenCV DNN SSD
        Returns list of (x, y, w, h)
        """
        if self.detector is None:
            return []
            
        (h, w) = image.shape[:2]
        
        # Resize to 300x300 for SSD
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
            (300, 300), (104.0, 177.0, 123.0))
            
        self.detector.setInput(blob)
        detections = self.detector.forward()
        
        faces = []
        
        # Debugging: Track max confidence
        max_conf = 0.0
        
        # Loop over detections
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > max_conf: max_conf = confidence
            
            if confidence > FACE_DETECTION_THRESHOLD:
                # Compute (x, y, w, h)
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (startX, startY, endX, endY) = box.astype("int")
                
                # CAST TO INT FOR JSON SERIALIZATION
                startX, startY, endX, endY = int(startX), int(startY), int(endX), int(endY)
                
                width = int(endX - startX)
                height = int(endY - startY)
                
                # Check min size
                if width < FACE_MIN_SIZE[0] or height < FACE_MIN_SIZE[1]:
                    continue
                    
                faces.append((startX, startY, width, height))
        
        if not faces:
            logger.info(f"No faces detected. Max conf: {max_conf:.3f} (Img: {w}x{h})")
                
        return faces

    def encode_face(self, image, face_rect):
        """
        Generate 128d embedding using SFace
        """
        if self.recognizer is None:
            return None
            
        (x, y, w, h) = face_rect
        (img_h, img_w) = image.shape[:2]
        
        # Safe crop
        x = max(0, x); y = max(0, y)
        w = min(w, img_w - x); h = min(h, img_h - y)
        
        face_roi = image[y:y+h, x:x+w]
        if face_roi.size == 0: return None
        
        # SFace Preprocessing: 112x112
        # blobFromImage performs mean subtraction and scaling
        # SFace expects BGR, 112x112
        faceBlob = cv2.dnn.blobFromImage(face_roi, 1.0, (112, 112), (0, 0, 0), swapRB=False)
            
        self.recognizer.setInput(faceBlob)
        vec = self.recognizer.forward()
        
        # Normalize vector for Cosine Similarity
        # SFace output is usually 128d
        norm_vec = vec / np.linalg.norm(vec)
        
        return {
            'encoding': norm_vec.flatten().tolist(),
            'version': 'opencv_sface_v1'
        }

    def recognize_faces(self, image):
        """
        Recognize faces using Cosine Similarity on SFace embeddings
        """
        faces = self.detect_faces(image)
        results = []
        
        if not faces:
            return []
            
        if not self.known_face_encodings:
            return [] # No training data
            
        known_encs = np.array(self.known_face_encodings) # Shape: (N, 128)
            
        for (x, y, w, h) in faces:
            # Encode
            encoding_data = self.encode_face(image, (x, y, w, h))
            if not encoding_data:
                continue
                
            input_vec = np.array(encoding_data['encoding']) # Shape: (128,)
            
            # Compute Cosine Similarity
            # Similarity = (A . B) / (||A|| * ||B||)
            # Since vectors are already normalized: Similarity = A . B
            
            # Dot product against all known encodings
            scores = np.dot(known_encs, input_vec) # Shape: (N,)
            
            best_idx = np.argmax(scores)
            max_score = scores[best_idx]
            
            student_id = None
            confidence = 0.0
            
            if max_score > FACE_MATCH_THRESHOLD:
                student_id = self.known_face_ids[best_idx]
                # Scale confidence: Threshold -> 50%, 1.0 -> 100%
                # (score - thresh) / (1 - thresh)
                norm_score = (max_score - FACE_MATCH_THRESHOLD) / (1.0 - FACE_MATCH_THRESHOLD)
                confidence = 50 + (norm_score * 50)
                confidence = min(100, max(0, confidence))
            else:
                 # Scale confidence: 0 -> 0%, Threshold -> 50%
                 confidence = (max_score / FACE_MATCH_THRESHOLD) * 50
            
            results.append({
                'rect': (x, y, w, h),
                'student_id': student_id,
                'confidence': round(confidence, 1),
                'score': round(float(max_score), 3),
                'distance': round(float(1.0 - max_score), 3) # for backward compat
            })
            
        return results

    def verify_face_quality(self, image, allow_multiple=False):
        faces = self.detect_faces(image)
        if len(faces) == 0: return False, "No face detected", []
        if len(faces) > 1 and not allow_multiple: return False, "Multiple faces", []
        return True, "OK", faces

    def save_face_image(self, image, student_id, face_rect):
        x, y, w, h = face_rect
        face_dir = os.path.join(settings.MEDIA_ROOT, 'faces', f'student_{student_id}')
        os.makedirs(face_dir, exist_ok=True)
        filename = f"face_{secrets.token_hex(8)}.jpg"
        filepath = os.path.join(face_dir, filename)
        
        # Add padding
        pad_h = int(h * 0.2)
        pad_w = int(w * 0.2)
        h_img, w_img = image.shape[:2]
        y1 = max(0, y - pad_h); y2 = min(h_img, y + h + pad_h)
        x1 = max(0, x - pad_w); x2 = min(w_img, x + w + pad_w)
        
        cv2.imwrite(filepath, image[y1:y2, x1:x2])
        return os.path.join('faces', f'student_{student_id}', filename)

    @staticmethod
    def base64_to_image(base64_string):
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]
        img_data = base64.b64decode(base64_string)
        nparr = np.frombuffer(img_data, np.uint8)
        return cv2.imdecode(nparr, cv2.IMREAD_COLOR)

# Global Instance
face_recognizer = FaceRecognizer()
