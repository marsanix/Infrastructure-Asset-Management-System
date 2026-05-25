"""Inisialisasi Flask extensions (tanpa app — pakai app factory)."""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db      = SQLAlchemy()
migrate = Migrate()
jwt     = JWTManager()

# Rate limiter — key berdasarkan IP (OWASP A07 - Auth Failures)
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
)
