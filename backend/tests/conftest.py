"""Shared test bootstrap."""
import base64
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

os.environ.setdefault('DATABASE_URL', f"sqlite:///{ROOT / 'tests' / 'test.db'}")
os.environ.setdefault('JWT_SECRET', 'test-secret-at-least-32-chars-long-for-jwt')
os.environ.setdefault('AES_KEY_BASE64', base64.b64encode(b'0' * 32).decode())
os.environ.setdefault('FRONTEND_ORIGIN', 'http://localhost:3000')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('COOKIE_SAMESITE', 'Lax')

# Test-harness invariants (forced, not setdefault):
# - The Flask test client operates over HTTP, so Secure cookies would not
#   round-trip — COOKIE_SECURE must be false for the test client regardless
#   of the deployment value (which is true for HTTPS/Nginx in production).
# - Tests fire many rapid requests; rate limiting must be disabled.
os.environ['COOKIE_SECURE'] = 'false'
os.environ['RATELIMIT_ENABLED'] = 'false'
