import sys
try:
    import cv2
    print("✓ OpenCV installed:", cv2.__version__)
except:
    print("✗ OpenCV NOT installed")
    print("  Install: pip install opencv-python")

try:
    import face_recognition
    print("✓ face_recognition installed")
except Exception as e:
    print("✗ face_recognition NOT installed:", e)
    print("  Install: pip install face-recognition")
    print("  Note: Requires Visual Studio Build Tools on Windows")
