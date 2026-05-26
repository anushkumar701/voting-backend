"""
OTP Manager for Voter Authentication
Handles OTP generation, verification, rate limiting
"""
import random
import time
import sqlite3
from datetime import datetime, timedelta

class OTPManager:
    def __init__(self, db_path="database/voting.db"):
        self.db_path = db_path
        self.OTP_EXPIRY_MINUTES = 5
        self.MAX_ATTEMPTS = 3
        self.LOCKOUT_MINUTES = 60
        self._init_otp_table()
    
    def _init_otp_table(self):
        """Initialize OTP tracking table"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS otp_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            voter_id TEXT NOT NULL,
            phone TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            attempts INTEGER DEFAULT 0,
            is_verified BOOLEAN DEFAULT 0,
            locked_until TIMESTAMP NULL
        )
        """)
        
        cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_otp_voter ON otp_sessions(voter_id, is_verified)
        """)
        
        conn.commit()
        conn.close()
    
    def _generate_otp(self):
        """Generate 6-digit OTP"""
        return str(random.randint(100000, 999999))
    
    def _is_locked(self, voter_id):
        """Check if voter is locked out"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
        SELECT locked_until FROM otp_sessions
        WHERE voter_id = ? AND locked_until IS NOT NULL
        ORDER BY created_at DESC LIMIT 1
        """, (voter_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            locked_until = datetime.fromisoformat(result[0])
            if datetime.now() < locked_until:
                remaining = (locked_until - datetime.now()).seconds // 60
                return True, remaining
        
        return False, 0
    
    def request_otp(self, voter_id, phone):
        """Generate and store OTP"""
        try:
            is_locked, remaining_minutes = self._is_locked(voter_id)
            if is_locked:
                return {
                    "success": False,
                    "message": f"Account locked. Try again in {remaining_minutes} minutes"
                }
            
            otp_code = self._generate_otp()
            expires_at = datetime.now() + timedelta(minutes=self.OTP_EXPIRY_MINUTES)
            
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            INSERT INTO otp_sessions (voter_id, phone, otp_code, expires_at)
            VALUES (?, ?, ?, ?)
            """, (voter_id, phone, otp_code, expires_at.isoformat()))
            
            conn.commit()
            conn.close()
            
            print(f"[OTP] Generated for {voter_id}: {otp_code}")
            
            return {
                "success": True,
                "message": f"OTP sent to {phone}",
                "otp_for_testing": otp_code,
                "expires_in_minutes": self.OTP_EXPIRY_MINUTES
            }
        
        except Exception as e:
            return {"success": False, "message": f"OTP generation error: {str(e)}"}
    
    def verify_otp(self, voter_id, otp_code):
        """Verify OTP and handle failed attempts"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            SELECT id, otp_code, expires_at, attempts, is_verified
            FROM otp_sessions
            WHERE voter_id = ? AND is_verified = 0
            ORDER BY created_at DESC LIMIT 1
            """, (voter_id,))
            
            result = cursor.fetchone()
            
            if not result:
                conn.close()
                return {"success": False, "message": "No OTP found. Request new OTP"}
            
            session_id, stored_otp, expires_at, attempts, is_verified = result
            
            expires_at = datetime.fromisoformat(expires_at)
            if datetime.now() > expires_at:
                conn.close()
                return {"success": False, "message": "OTP expired. Request new OTP"}
            
            if attempts >= self.MAX_ATTEMPTS:
                locked_until = datetime.now() + timedelta(minutes=self.LOCKOUT_MINUTES)
                cursor.execute("""
                UPDATE otp_sessions SET locked_until = ? WHERE id = ?
                """, (locked_until.isoformat(), session_id))
                conn.commit()
                conn.close()
                return {"success": False, "message": f"Too many failed attempts. Locked for {self.LOCKOUT_MINUTES} minutes"}
            
            if otp_code != stored_otp:
                cursor.execute("""
                UPDATE otp_sessions SET attempts = attempts + 1 WHERE id = ?
                """, (session_id,))
                conn.commit()
                remaining = self.MAX_ATTEMPTS - attempts - 1
                conn.close()
                return {"success": False, "message": f"Invalid OTP. {remaining} attempts remaining"}
            
            cursor.execute("""
            UPDATE otp_sessions SET is_verified = 1 WHERE id = ?
            """, (session_id,))
            conn.commit()
            conn.close()
            
            return {"success": True, "message": "OTP verified successfully"}
        
        except Exception as e:
            return {"success": False, "message": f"Verification error: {str(e)}"}
    
    def cleanup_expired(self):
        """Remove expired OTP sessions"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
            DELETE FROM otp_sessions
            WHERE expires_at < ? AND is_verified = 0
            """, (datetime.now().isoformat(),))
            
            deleted = cursor.rowcount
            conn.commit()
            conn.close()
            
            return deleted
        except Exception as e:
            print(f"Cleanup error: {e}")
            return 0
