
import os
import django
import sys

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RollVision.settings')
django.setup()

from dashboard.models import Student
from dashboard.face_utils import face_recognizer
import logging

# Configure logging to stdout
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_debug_training():
    print("--- Starting Debug Training ---")
    
    # 1. Check students
    students = Student.objects.exclude(photo='')
    print(f"Found {students.count()} students with photos.")
    
    training_data = []
    for s in students:
        if s.photo:
            print(f"Adding student {s.student_id} with photo: {s.photo.path}")
            training_data.append({
                'student_id': s.student_id,
                'image_path': s.photo.path
            })
    
    if not training_data:
        print("ERROR: No training data available!")
        return
        
    print(f"Calling train_model with {len(training_data)} items...")
    
    try:
        success = face_recognizer.train_model(training_data)
        if success:
            print("SUCCESS: Model trained successfully.")
            from django.conf import settings
            model_path = os.path.join(settings.MEDIA_ROOT, 'trainer.yml')
            if os.path.exists(model_path):
                print(f"VERIFIED: trainer.yml exists at {model_path}")
            else:
                print(f"ERROR: trainer.yml NOT found at {model_path} despite success return!")
        else:
            print("FAILURE: train_model returned False.")
            
    except Exception as e:
        print(f"EXCEPTION during training: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    run_debug_training()
