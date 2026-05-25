"""Konfigurasi aplikasi per environment."""
import os
from datetime import timedelta


class BaseConfig:
    # Flask
    SECRET_KEY: str = os.environ["SECRET_KEY"]
    JSON_SORT_KEYS = False

    # Database — gunakan parameterized query via SQLAlchemy (OWASP A03)
    SQLALCHEMY_DATABASE_URI: str = (
        f"postgresql+psycopg2://"
        f"{os.environ['POSTGRES_USER']}:{os.environ['POSTGRES_PASSWORD']}"
        f"@{os.environ['POSTGRES_HOST']}:{os.environ.get('POSTGRES_PORT', '5432')}"
        f"/{os.environ['POSTGRES_DB']}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    # JWT
    JWT_SECRET_KEY: str = os.environ["JWT_SECRET_KEY"]
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRES  = timedelta(
        minutes=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "15"))
    )
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(
        days=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "7"))
    )
    JWT_TOKEN_LOCATION = ["headers"]
    JWT_HEADER_NAME    = "Authorization"
    JWT_HEADER_TYPE    = "Bearer"

    # Redis (rate limiting + token blacklist)
    REDIS_URL: str = (
        f"redis://:{os.environ['REDIS_PASSWORD']}"
        f"@{os.environ['REDIS_HOST']}:{os.environ.get('REDIS_PORT', '6379')}/0"
    )
    RATELIMIT_STORAGE_URI: str = REDIS_URL
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "200 per day;50 per hour")

    # CORS
    CORS_ORIGINS: list[str] = [
        o.strip() for o in os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
    ]

    # AES key untuk asset credentials
    AES_ENCRYPTION_KEY: str = os.environ["AES_ENCRYPTION_KEY"]

    # Brute-force protection
    MAX_LOGIN_ATTEMPTS = 5


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    SQLALCHEMY_ECHO = False  # set True untuk debug query


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG   = False
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(minutes=5)
    # Nonaktifkan rate-limiter dan Redis storage agar test tidak perlu Redis nyata
    RATELIMIT_ENABLED      = False
    RATELIMIT_STORAGE_URI  = "memory://"


config_map = {
    "development": DevelopmentConfig,
    "production":  ProductionConfig,
    "testing":     TestingConfig,
}
