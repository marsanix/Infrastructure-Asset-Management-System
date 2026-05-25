"""
Token blacklist menggunakan Redis.
Digunakan untuk invalidate JWT saat logout (OWASP A07).
"""
import redis
from flask import current_app


def _get_redis() -> redis.Redis:
    return redis.from_url(current_app.config["REDIS_URL"], decode_responses=True)


def revoke_token(jti: str, expires_in_seconds: int) -> None:
    """Masukkan JTI ke blacklist dengan TTL sesuai expiry token."""
    r = _get_redis()
    r.setex(f"revoked_jti:{jti}", expires_in_seconds, "1")


def is_token_revoked(jti: str) -> bool:
    """Cek apakah token sudah di-revoke."""
    r = _get_redis()
    return r.exists(f"revoked_jti:{jti}") == 1
