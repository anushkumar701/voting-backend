"""
OTP generation, delivery (console-based), verification, resend, lockout.
"""
import random
import time
from database.db_setup import (
    store_otp, get_latest_otp, mark_otp_used,
    is_voter_locked, record_failed_attempt, reset_login_attempts
)
from utils import rate_limiter

OTP_TTL = 300          # 5 minutes
MAX_ATTEMPTS = 3
LOCKOUT_SECONDS = 3600 # 1 hour


def _generate_code():
    return str(random.randint(100000, 999999))


def request_otp(voter_id):
    """
    Generate + store OTP.  Returns the code so the backend can print/send it.
    Rate-limited: max 3 requests per 60 s per voter.
    """
    # TEMPORARILY DISABLED - causing hangs
    # if not rate_limiter.is_allowed(f"otp_req:{voter_id}", max_requests=3, window_seconds=60):
    #     return {"success": False, "message": "Too many OTP requests. Wait a moment."}

    locked, remaining = is_voter_locked(voter_id)
    if locked:
        return {"success": False, "message": f"Account locked. Try again in {remaining}s."}

    code = _generate_code()
    store_otp(voter_id, code, ttl_seconds=OTP_TTL)
    print(f"[OTP] voter={voter_id}  code={code}  ttl={OTP_TTL}s")
    return {"success": True, "otp": code, "expires_in": OTP_TTL}


def verify_otp(voter_id, submitted_code):
    """
    Verify submitted OTP.
    Tracks failed attempts → lockout after MAX_ATTEMPTS.
    """
    locked, remaining = is_voter_locked(voter_id)
    if locked:
        return {"success": False, "message": f"Account locked. Try again in {remaining}s."}

    otp_row = get_latest_otp(voter_id)

    # No active OTP exists
    if not otp_row:
        record_failed_attempt(voter_id)
        return {"success": False, "message": "No active OTP. Request a new one."}

    # Expired?
    if time.time() > otp_row["expires_at"]:
        mark_otp_used(otp_row["id"])
        record_failed_attempt(voter_id)
        return {"success": False, "message": "OTP expired. Request a new one."}

    # Wrong code?
    if str(otp_row["otp_code"]).strip() != str(submitted_code).strip():
        count = record_failed_attempt(voter_id)
        if count >= MAX_ATTEMPTS:
            return {"success": False, "message": "Account locked for 1 hour due to too many failed attempts."}
        return {"success": False, "message": f"Invalid OTP. {MAX_ATTEMPTS - count} attempt(s) left."}

    # ✓ correct
    mark_otp_used(otp_row["id"])
    reset_login_attempts(voter_id)
    rate_limiter.reset(f"otp_req:{voter_id}")
    return {"success": True, "message": "OTP verified"}
