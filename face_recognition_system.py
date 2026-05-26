"""
Face Recognition System for E-Voting
Handles registration and verification with robust error handling
"""
import cv2
import face_recognition
import numpy as np
import pickle
import os
from pathlib import Path

class FaceRecognitionSystem:
    def __init__(self, storage_dir="face_data"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        self.MIN_ACCURACY = 60.0
        self.MIN_BRIGHTNESS = 40
        self.MIN_BLUR_THRESHOLD = 100
        self.MIN_FACE_SIZE = 80
        self.MAX_FACE_SIZE = 500
        
    def _check_image_quality(self, image):
        """Check if image meets quality requirements"""
        if image is None or image.size == 0:
            return False, "Invalid image"
        
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        
        if brightness < self.MIN_BRIGHTNESS:
            return False, "Image too dark"
        
        blur = cv2.Laplacian(gray, cv2.CV_64F).var()
        if blur < self.MIN_BLUR_THRESHOLD:
            return False, "Image too blurry"
        
        return True, "Quality OK"
    
    def _validate_face_size(self, face_location, image_shape):
        """Check if detected face size is reasonable"""
        top, right, bottom, left = face_location
        face_width = right - left
        face_height = bottom - top
        
        if face_width < self.MIN_FACE_SIZE or face_height < self.MIN_FACE_SIZE:
            return False, "Face too small"
        
        if face_width > self.MAX_FACE_SIZE or face_height > self.MAX_FACE_SIZE:
            return False, "Face too large or too close"
        
        return True, "Size OK"
    
    def register_face(self, image_path_or_array, voter_id):
        """
        Register voter face from image
        Returns: (success, message, encoding)
        """
        try:
            if isinstance(image_path_or_array, str):
                if not os.path.exists(image_path_or_array):
                    return False, "Image file not found", None
                image = cv2.imread(image_path_or_array)
            else:
                image = image_path_or_array
            
            if image is None:
                return False, "Failed to load image", None
            
            quality_ok, quality_msg = self._check_image_quality(image)
            if not quality_ok:
                return False, quality_msg, None
            
            rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            face_locations = face_recognition.face_locations(rgb_image, model="hog")
            
            if len(face_locations) == 0:
                return False, "No face detected in image", None
            
            if len(face_locations) > 1:
                return False, "Multiple faces detected. Only one face allowed", None
            
            size_ok, size_msg = self._validate_face_size(face_locations[0], image.shape)
            if not size_ok:
                return False, size_msg, None
            
            face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
            
            if len(face_encodings) == 0:
                return False, "Failed to extract face features", None
            
            encoding = face_encodings[0]
            
            encoding_file = self.storage_dir / f"{voter_id}_encoding.pkl"
            with open(encoding_file, 'wb') as f:
                pickle.dump(encoding, f)
            
            info_file = self.storage_dir / f"{voter_id}_info.txt"
            with open(info_file, 'w') as f:
                f.write(f"Voter ID: {voter_id}\n")
                f.write(f"Encoding shape: {encoding.shape}\n")
                f.write(f"Registration: Success\n")
            
            return True, "Face registered successfully", encoding
            
        except Exception as e:
            return False, f"Registration error: {str(e)}", None
    
    def _calculate_accuracy(self, distance):
        """
        Convert face distance to accuracy percentage
        Distance range: 0.0 (perfect) to 1.0+ (different)
        Threshold: 0.6 is standard
        """
        if distance > 1.0:
            return 0.0
        
        accuracy = max(0, (1.0 - distance) * 100)
        return round(accuracy, 2)
    
    def verify_face_live(self, voter_id, duration_seconds=10):
        """
        Verify voter face using live webcam
        Returns: (success, accuracy, message)
        """
        try:
            encoding_file = self.storage_dir / f"{voter_id}_encoding.pkl"
            
            if not encoding_file.exists():
                return False, 0.0, "No registered face found for this voter"
            
            with open(encoding_file, 'rb') as f:
                stored_encoding = pickle.load(f)
            
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                return False, 0.0, "Cannot access webcam. Check permissions"
            
            cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            cap.set(cv2.CAP_PROP_FPS, 30)
            
            print(f"\n{'='*60}")
            print("LIVE FACE VERIFICATION")
            print(f"{'='*60}")
            print(f"Voter ID: {voter_id}")
            print(f"Duration: {duration_seconds} seconds")
            print(f"Minimum required accuracy: {self.MIN_ACCURACY}%")
            print(f"{'='*60}\n")
            
            frame_count = 0
            max_frames = duration_seconds * 10
            best_accuracy = 0.0
            verification_attempts = []
            
            while frame_count < max_frames:
                ret, frame = cap.read()
                
                if not ret:
                    continue
                
                frame_count += 1
                
                quality_ok, quality_msg = self._check_image_quality(frame)
                
                display_frame = frame.copy()
                status_color = (0, 255, 255)
                status_text = "Detecting face..."
                
                if not quality_ok:
                    status_color = (0, 0, 255)
                    status_text = quality_msg
                else:
                    small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
                    rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                    
                    face_locations = face_recognition.face_locations(rgb_small_frame, model="hog")
                    
                    if len(face_locations) == 0:
                        status_color = (0, 165, 255)
                        status_text = "No face detected"
                    elif len(face_locations) > 1:
                        status_color = (0, 0, 255)
                        status_text = "Multiple faces detected"
                    else:
                        top, right, bottom, left = face_locations[0]
                        top, right, bottom, left = top*2, right*2, bottom*2, left*2
                        
                        size_ok, size_msg = self._validate_face_size((top, right, bottom, left), frame.shape)
                        
                        if not size_ok:
                            status_color = (0, 165, 255)
                            status_text = size_msg
                            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 165, 255), 2)
                        else:
                            cv2.rectangle(display_frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            
                            if frame_count % 3 == 0:
                                face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
                                
                                if len(face_encodings) > 0:
                                    live_encoding = face_encodings[0]
                                    distance = face_recognition.face_distance([stored_encoding], live_encoding)[0]
                                    accuracy = self._calculate_accuracy(distance)
                                    
                                    verification_attempts.append(accuracy)
                                    
                                    if accuracy > best_accuracy:
                                        best_accuracy = accuracy
                                    
                                    if accuracy >= self.MIN_ACCURACY:
                                        status_color = (0, 255, 0)
                                        status_text = f"MATCH: {accuracy}%"
                                    else:
                                        status_color = (0, 165, 255)
                                        status_text = f"Accuracy: {accuracy}%"
                                    
                                    cv2.putText(display_frame, f"Best: {best_accuracy}%", 
                                              (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
                cv2.putText(display_frame, status_text, (10, 30), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, status_color, 2)
                
                progress = int((frame_count / max_frames) * 100)
                cv2.rectangle(display_frame, (10, 60), (630, 80), (50, 50, 50), -1)
                cv2.rectangle(display_frame, (10, 60), (10 + int(620 * progress / 100), 80), status_color, -1)
                cv2.putText(display_frame, f"Progress: {progress}%", (10, 100), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                
                cv2.imshow('Face Verification', display_frame)
                
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    break
            
            cap.release()
            cv2.destroyAllWindows()
            
            if len(verification_attempts) == 0:
                return False, 0.0, "No valid face detected during verification"
            
            avg_accuracy = np.mean(verification_attempts)
            final_accuracy = max(best_accuracy, avg_accuracy)
            
            print(f"\n{'='*60}")
            print("VERIFICATION RESULTS")
            print(f"{'='*60}")
            print(f"Attempts: {len(verification_attempts)}")
            print(f"Best accuracy: {best_accuracy}%")
            print(f"Average accuracy: {round(avg_accuracy, 2)}%")
            print(f"Final accuracy: {final_accuracy}%")
            print(f"Threshold: {self.MIN_ACCURACY}%")
            
            if final_accuracy >= self.MIN_ACCURACY:
                print(f"Status: ✓ VERIFIED")
                print(f"{'='*60}\n")
                return True, final_accuracy, "Face verified successfully"
            else:
                print(f"Status: ✗ FAILED")
                print(f"{'='*60}\n")
                return False, final_accuracy, f"Verification failed. Accuracy {final_accuracy}% < {self.MIN_ACCURACY}%"
        
        except Exception as e:
            if 'cap' in locals():
                cap.release()
            cv2.destroyAllWindows()
            return False, 0.0, f"Verification error: {str(e)}"
    
    def load_encoding(self, voter_id):
        """Load stored face encoding for a voter"""
        try:
            encoding_file = self.storage_dir / f"{voter_id}_encoding.pkl"
            if not encoding_file.exists():
                return None
            with open(encoding_file, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading encoding: {e}")
            return None
    
    def delete_face_data(self, voter_id):
        """Delete face data for a voter"""
        try:
            encoding_file = self.storage_dir / f"{voter_id}_encoding.pkl"
            info_file = self.storage_dir / f"{voter_id}_info.txt"
            
            deleted = False
            if encoding_file.exists():
                encoding_file.unlink()
                deleted = True
            if info_file.exists():
                info_file.unlink()
                deleted = True
            
            return deleted, "Face data deleted" if deleted else "No face data found"
        except Exception as e:
            return False, f"Error deleting face data: {str(e)}"


def test_registration():
    """Test face registration"""
    print("\n" + "="*60)
    print("TESTING FACE REGISTRATION")
    print("="*60)
    
    system = FaceRecognitionSystem()
    
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("ERROR: Cannot access webcam")
        return False
    
    print("Position your face in the frame...")
    print("Press SPACE to capture image")
    print("Press Q to quit")
    
    captured = False
    while not captured:
        ret, frame = cap.read()
        if not ret:
            continue
        
        cv2.putText(frame, "Press SPACE to capture", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.imshow('Capture Face', frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):
            success, message, encoding = system.register_face(frame, "TEST_VOTER")
            print(f"\nResult: {message}")
            if success:
                print(f"Encoding shape: {encoding.shape}")
                captured = True
            break
        elif key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    return captured


def test_verification():
    """Test face verification"""
    print("\n" + "="*60)
    print("TESTING FACE VERIFICATION")
    print("="*60)
    
    system = FaceRecognitionSystem()
    
    encoding_file = Path("face_data/TEST_VOTER_encoding.pkl")
    if not encoding_file.exists():
        print("ERROR: No registered face found. Run registration first.")
        return False
    
    success, accuracy, message = system.verify_face_live("TEST_VOTER", duration_seconds=10)
    
    print(f"\nFinal Result:")
    print(f"  Success: {success}")
    print(f"  Accuracy: {accuracy}%")
    print(f"  Message: {message}")
    
    return success


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "register":
            test_registration()
        elif sys.argv[1] == "verify":
            test_verification()
        else:
            print("Usage: python face_recognition_system.py [register|verify]")
    else:
        print("\nFace Recognition System for E-Voting")
        print("="*60)
        print("Available commands:")
        print("  python face_recognition_system.py register  - Test registration")
        print("  python face_recognition_system.py verify    - Test verification")
        print("="*60)
