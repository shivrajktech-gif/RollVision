import face_recognition
import numpy as np
import cv2

print("Testing copy to zeros...")

path = r"c:\Users\aades\OneDrive\Desktop\DJANGO - Copy\folder\project\RollVision\media\faces\student_1\face_1.jpg"
img = cv2.imread(path)

if img is None:
    print("❌ Failed to read image")
else:
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Resize to 100x100
    small = cv2.resize(rgb, (100, 100))
    
    # Create Zeros
    container = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Copy data
    container[:] = small[:]
    
    print(f"Container Flags: {container.flags['C_CONTIGUOUS']}")
    
    try:
        face_recognition.face_locations(container, model="hog")
        print("✅ Copy to Zeros Success")
    except Exception as e:
        print(f"❌ Copy to Zeros Failed: {e}")

    # Test Random
    rand_img = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    try:
        face_recognition.face_locations(rand_img, model="hog")
        print("✅ Random Success")
    except Exception as e:
        print(f"❌ Random Failed: {e}")
