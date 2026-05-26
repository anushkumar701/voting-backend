import face_recognition
import numpy as np
import base64
import io
from PIL import Image, ImageStat
import os

FACE_DATA_DIR = os.path.join(os.path.dirname(__file__), 'face_data')

if not os.path.exists(FACE_DATA_DIR):
    os.makedirs(FACE_DATA_DIR)

def analyze_image_quality(image_array):
    """Analyze image quality and face position"""
    img = Image.fromarray(image_array)
    stat = ImageStat.Stat(img.convert('L'))
    brightness = stat.mean[0]
    
    warnings = []
    
    if brightness < 60:
        warnings.append("LOW_LIGHT")
    elif brightness > 200:
        warnings.append("TOO_BRIGHT")
    
    h, w = image_array.shape[:2]
    face_locations = face_recognition.face_locations(image_array)
    
    if len(face_locations) == 0:
        warnings.append("NO_FACE")
        return {"quality_ok": False, "warnings": warnings}
    
    if len(face_locations) > 1:
        warnings.append("MULTIPLE_FACES")
        return {"quality_ok": False, "warnings": warnings}
    
    top, right, bottom, left = face_locations[0]
    face_width = right - left
    face_height = bottom - top
    
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    
    if abs(center_x - w/2) > w * 0.2 or abs(center_y - h/2) > h * 0.2:
        warnings.append("NOT_CENTERED")
    
    if face_width < w * 0.2 or face_height < h * 0.2:
        warnings.append("TOO_FAR")
    elif face_width > w * 0.7 or face_height > h * 0.7:
        warnings.append("TOO_CLOSE")
    
    quality_ok = len(warnings) == 0
    return {"quality_ok": quality_ok, "warnings": warnings, "brightness": brightness}

def register_face(user_id, image_base64):
    try:
        image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        image_array = np.array(image)
        
        quality = analyze_image_quality(image_array)
        if not quality['quality_ok']:
            return {"success": False, "message": f"Image quality issues: {', '.join(quality['warnings'])}"}
        
        face_encodings = face_recognition.face_encodings(image_array)
        
        if len(face_encodings) == 0:
            return {"success": False, "message": "No face detected"}
        
        face_encoding = face_encodings[0]
        encoding_file = os.path.join(FACE_DATA_DIR, f"{user_id}.npy")
        np.save(encoding_file, face_encoding)
        
        return {"success": True, "message": "Face registered successfully"}
        
    except Exception as e:
        return {"success": False, "message": f"Error: {str(e)}"}

def verify_face(user_id, image_base64):
    try:
        encoding_file = os.path.join(FACE_DATA_DIR, f"{user_id}.npy")
        
        if not os.path.exists(encoding_file):
            return {"success": False, "message": "No face registered", "verified": False, "confidence": 0}
        
        stored_encoding = np.load(encoding_file)
        
        image_data = base64.b64decode(image_base64.split(',')[1] if ',' in image_base64 else image_base64)
        image = Image.open(io.BytesIO(image_data))
        image = image.convert('RGB')
        image_array = np.array(image)
        
        quality = analyze_image_quality(image_array)
        
        face_encodings = face_recognition.face_encodings(image_array)
        
        if len(face_encodings) == 0:
            return {
                "success": True,
                "verified": False,
                "confidence": 0,
                "message": "No face detected",
                "quality": quality
            }
        
        current_encoding = face_encodings[0]
        
        face_distance = face_recognition.face_distance([stored_encoding], current_encoding)
        confidence = round((1 - face_distance[0]) * 100, 2)
        
        if confidence >= 60:
            verified = True
            message = f"Face verified: {confidence}% match"
        else:
            verified = False
            message = f"Face mismatch: {confidence}% (min 60% required)"
        
        return {
            "success": True,
            "verified": verified,
            "confidence": confidence,
            "message": message,
            "quality": quality
        }
            
    except Exception as e:
        return {"success": False, "verified": False, "confidence": 0, "message": str(e)}

def delete_face(user_id):
    try:
        encoding_file = os.path.join(FACE_DATA_DIR, f"{user_id}.npy")
        if os.path.exists(encoding_file):
            os.remove(encoding_file)
            return {"success": True, "message": "Face deleted"}
        return {"success": False, "message": "No face found"}
    except Exception as e:
        return {"success": False, "message": str(e)}
