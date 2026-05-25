"""Application factory — IAMS Backend."""
import os
from flask import Flask
from flask_cors import CORS
from flask_talisman import Talisman

from .extensions import db, migrate, jwt, limiter
from .config import config_map
from .utils.audit import register_audit_hooks


def create_app(config_name: str | None = None) -> Flask:
    if config_name is None:
        config_name = os.getenv("FLASK_ENV", "production")

    app = Flask(__name__)
    app.config.from_object(config_map[config_name])

    # ── Security Headers (OWASP A05) ──────────────────────────
    # Content-Security-Policy, HSTS, X-Frame-Options, dll.
    # CSP ketat — IBM Plex Sans self-hosted via @fontsource
    # Tidak ada fonts.googleapis.com atau CDN eksternal (OWASP A05)
    # 'unsafe-inline' di style-src hanya untuk Tailwind utility classes
    # Idealnya pakai nonce-based CSP di production
    csp = {
        "default-src":   "'self'",
        "script-src":    "'self'",
        "style-src":     "'self' 'unsafe-inline'",
        "img-src":       "'self' data:",
        "font-src":      "'self'",   # @fontsource fonts served dari /assets/
        "connect-src":   "'self'",
        "frame-src":     "'none'",
        "frame-ancestors": "'none'",
        "object-src":    "'none'",
        "base-uri":      "'self'",
        "form-action":   "'self'",
    }
    Talisman(
        app,
        content_security_policy=csp,
        force_https=False,  # development: HTTP. Set True di production dengan HTTPS
        strict_transport_security=config_name == "production",
        strict_transport_security_max_age=31536000,
        referrer_policy="strict-origin-when-cross-origin",
        feature_policy={
            "geolocation": "'none'",
            "microphone":  "'none'",
            "camera":      "'none'",
        },
    )

    # ── CORS (hanya izinkan origin yang terdaftar) ─────────────
    CORS(
        app,
        origins=app.config["CORS_ORIGINS"],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # ── Extensions ────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    limiter.init_app(app)

    # ── JWT token blacklist check (logout / revoke) ────────────
    from .utils.token_store import is_token_revoked
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        return is_token_revoked(jwt_payload["jti"])

    # ── Register Blueprints ───────────────────────────────────
    from .api.v1 import api_v1
    app.register_blueprint(api_v1, url_prefix="/api/v1")

    # ── Health check ──────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok"}, 200

    # ── Audit hooks ───────────────────────────────────────────
    register_audit_hooks(app)

    return app
