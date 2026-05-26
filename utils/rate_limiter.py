"""
In-memory rate limiter.
Used for OTP requests and login endpoints.
"""
import time
import threading

_lock = threading.Lock()
_buckets = {}          # key -> { tokens, last_refill }


def _get_bucket(key, max_requests, window_seconds):
    now = time.time()
    with _lock:
        if key not in _buckets:
            _buckets[key] = {"tokens": max_requests, "last_refill": now}
        bucket = _buckets[key]
        elapsed = now - bucket["last_refill"]
        if elapsed >= window_seconds:
            bucket["tokens"] = max_requests
            bucket["last_refill"] = now
        return bucket


def is_allowed(key, max_requests=5, window_seconds=60):
    """
    Returns True if the request is allowed, False if rate-limited.
    key: unique identifier (e.g. voter_id, IP)
    max_requests: allowed calls in window
    window_seconds: sliding window size
    """
    with _lock:
        bucket = _get_bucket(key, max_requests, window_seconds)
        if bucket["tokens"] > 0:
            bucket["tokens"] -= 1
            return True
        return False


def reset(key):
    """Force-reset a specific key (e.g. after successful auth)."""
    with _lock:
        _buckets.pop(key, None)
