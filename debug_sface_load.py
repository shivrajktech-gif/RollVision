import cv2
import os

model_path = r"c:\Users\aades\OneDrive\Desktop\DJANGO - Copy\folder\project\RollVision\dashboard\models\face_recognition_sface_2021dec.onnx"

print(f"Checking model at: {model_path}")
if not os.path.exists(model_path):
    print("❌ File does not exist!")
else:
    print(f"File size: {os.path.getsize(model_path)} bytes")
    
print("Attempting to load with cv2.dnn.readNetFromONNX...")
try:
    net = cv2.dnn.readNetFromONNX(model_path)
    print("✅ Success! Model loaded.")
except Exception as e:
    print(f"❌ Failed to load model: {e}")
