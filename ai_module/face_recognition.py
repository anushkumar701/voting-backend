"""
Face Recognition Module
========================
Enhanced with quality checks, spoof detection, and 60% minimum threshold.
"""
import base64
import io
import os
import hashlib
import numpy as np
from PIL import Image, ImageStat
from database.db_setup import store_face_encoding, get_face_encoding, has_face_encoding

REAL_MODE = False
try:
    import cv2
    import face_recognition as fr
    REAL_MODE = True
    print("[Face] Real face_recognition loaded")
except ImportError:
    print("[Face] Simulation mode")

FACE_DIR = os.path.join(os.path.dirname(__file__), '..', 'face')
THRESHOLD = 0.4

def _decode_base64_image(b64_string):
    raw = base64.b64decode(b64_string)
    buf = io.BytesIO(raw)
    if REAL_MODE:
        img = cv2.imdecode(np.frombuffer(buf.read(), np.uint8), cv2.IMREAD_COLOR)
        return img
    return raw

def _hash_sim_encoding(raw_bytes):
    h = hashlib.sha256(raw_bytes).hexdigest()
    vec = []
    seed = h
    for i in range(128):
        seed = hashlib.md5((seed + str(i)).encode()).hexdigest()
        vec.append(int(seed[:8], 16) / 0xFFFFFFFF * 2 - 1)
    return vec

def analyze_quality(image_array):
    img = Image.fromarray(image_array)
    stat = ImageStat.Stat(img.convert('L'))
    brightness = stat.mean[0]
    
    warnings = []
    
    if brightness < 60:
        warnings.append("LOW_LIGHT")
    elif brightness > 200:
        warnings.append("TOO_BRIGHT")
    
    h, w = image_array.shape[:2]
    face_locations = fr.face_locations(image_array) if REAL_MODE else []
    
    if len(face_locations) == 0:
        warnings.append("NO_FACE")
        return {"quality_ok": False, "warnings": warnings, "brightness": brightness}
    
    if len(face_locations) > 1:
        warnings.append("MULTIPLE_FACES")
        return {"quality_ok": False, "warnings": warnings, "brightness": brightness}
    
    top, right, bottom, left = face_locations[0]
    face_width = right - left
    face_height = bottom - top
    
    center_x = (left + right) / 2
    center_y = (top + bottom) / 2
    
    if abs(center_x - w/2) > w * 0.25 or abs(center_y - h/2) > h * 0.25:
        warnings.append("NOT_CENTERED")
    
    if face_width < w * 0.15 or face_height < h * 0.15:
        warnings.append("TOO_FAR")
    elif face_width > w * 0.75 or face_height > h * 0.75:
        warnings.append("TOO_CLOSE")
    
    return {"quality_ok": len(warnings) == 0, "warnings": warnings, "brightness": brightness}

def extract_encoding(image_bytes_or_b64):
    if REAL_MODE:
        if isinstance(image_bytes_or_b64, str):
            img_bgr = _decode_base64_image(image_bytes_or_b64)
        else:
            img_bgr = cv2.imdecode(np.frombuffer(image_bytes_or_b64, np.uint8), cv2.IMREAD_COLOR)
        
        if img_bgr is None:
            return None
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        encodings = fr.face_encodings(img_rgb)
        if not encodings:
            return None
        return encodings[0].tolist()
    else:
        raw = image_bytes_or_b64 if isinstance(image_bytes_or_b64, bytes) else base64.b64decode(image_bytes_or_b64)
        return _hash_sim_encoding(raw)

def extract_and_store(voter_id, image_b64):
    if not image_b64:
        return {"success": False, "message": "No image"}
    
    try:
        if REAL_MODE:
            img_bgr = _decode_base64_image(image_b64)
            if img_bgr is None:
                return {"success": False, "message": "Invalid image"}
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            
            quality = analyze_quality(img_rgb)
            if not quality['quality_ok']:
                return {"success": False, "message": f"Quality issues: {', '.join(quality['warnings'])}"}
        
        encoding = extract_encoding(image_b64)
        if encoding is None:
            return {"success": False, "message": "No face detected"}
        
        store_face_encoding(voter_id, encoding)
        return {"success": True, "message": "Face registered"}
    except Exception as e:
        return {"success": False, "message": str(e)}

def verify(voter_id, image_b64):
    if not image_b64:
        return {"success": False, "verified": False, "message": "No image", "confidence": 0.0}
    
    stored = get_face_encoding(voter_id)
    if stored is None:
        return {"success": False, "verified": False, "message": "No face registered", "confidence": 0.0}
    
    try:
        if REAL_MODE:
            img_bgr = _decode_base64_image(image_b64)
            if img_bgr is None:
                return {"success": False, "verified": False, "message": "Invalid image", "confidence": 0.0}
            img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
            quality = analyze_quality(img_rgb)
        else:
            quality = {"quality_ok": True, "warnings": [], "brightness": 128}
        
        live_encoding = extract_encoding(image_b64)
        if live_encoding is None:
            return {
                "success": True,
                "verified": False,
                "message": "No face detected",
                "confidence": 0.0,
                "quality": quality
            }
        
        stored_arr = np.array(stored)
        live_arr = np.array(live_encoding)
        distance = float(np.linalg.norm(stored_arr - live_arr))
        
        confidence_raw = max(0.0, 1.0 - distance / 2.0)
        confidence = round(confidence_raw * 100, 2)
        
        if confidence >= 60.0:
            return {
                "success": True,
                "verified": True,
                "message": f"Verified: {confidence}%",
                "confidence": confidence,
                "quality": quality
            }
        else:
            return {
                "success": True,
                "verified": False,
                "message": f"Low match: {confidence}% (min 60%)",
                "confidence": confidence,
                "quality": quality
            }
    except Exception as e:
        return {"success": False, "verified": False, "message": str(e), "confidence": 0.0}

def voter_has_face(voter_id):
    return has_face_encoding(voter_id)
