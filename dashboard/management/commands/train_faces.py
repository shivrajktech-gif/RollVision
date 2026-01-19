from django.core.management.base import BaseCommand
from dashboard.models import Student, FaceEncoding
from dashboard.face_utils import face_recognizer
import cv2
import json
import os
import logging
from django.conf import settings

# Configure logger
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Regenerates 128d OpenFace/Dlib encodings for all students from their photos'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting Deep Learning Encoding Regeneration...")
        
        students = Student.objects.all()
        # Optionally clear old encodings if you want a fresh start
        # FaceEncoding.objects.all().delete()
        
        count = 0
        success_count = 0
        
        for s in students:
            self.stdout.write(f"Processing {s.student_id}...")
            
            # Find the best image
            image_path = None
            
            # 1. Try Main Photo
            if s.photo and os.path.exists(s.photo.path):
                image_path = s.photo.path
            
            # 2. Try Faces Directory if main photo missing
            if not image_path:
                faces_dir = os.path.join(settings.MEDIA_ROOT, 'faces', f'student_{s.student_id}')
                if os.path.exists(faces_dir):
                    images = [f for f in os.listdir(faces_dir) if f.lower().endswith(('jpg', 'png'))]
                    if images:
                        image_path = os.path.join(faces_dir, images[0])
            
            if not image_path:
                self.stdout.write(self.style.WARNING(f"  - No image found for {s.student_id}"))
                continue
                
            # Process Image
            try:
                # Check if encoding already exists to save time (optional)
                # if FaceEncoding.objects.filter(student=s).exists():
                #     self.stdout.write(f"  - Encoding already exists.")
                #     continue

                image = cv2.imread(image_path)
                if image is None:
                    continue
                
                # Detect and Encode
                # Use Dlib HOG (default in `detect_faces`)
                faces = face_recognizer.detect_faces(image)
                
                if not faces:
                    self.stdout.write(self.style.WARNING(f"  - No face detected in image for {s.student_id}"))
                    continue
                
                # Take largest face
                largest_face = max(faces, key=lambda r: r[2] * r[3])
                
                # Generate Encoding
                encoding_data = face_recognizer.encode_face(image, largest_face)
                
                if encoding_data:
                    # Save/Update Encoding
                    FaceEncoding.objects.update_or_create(
                        student=s,
                        defaults={
                            'encoding_data': json.dumps(encoding_data),
                            'image_path': image_path,
                            'is_active': True
                        }
                    )
                    s.is_trained = True
                    s.save()
                    success_count += 1
                    self.stdout.write(self.style.SUCCESS(f"  + encoded successfully"))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  ! Error: {e}"))
        
        # Reload cache
        face_recognizer.refresh_encodings()
        self.stdout.write(self.style.SUCCESS(f"\nCompleted. Generated encodings for {success_count}/{len(students)} students."))
