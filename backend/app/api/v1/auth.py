"""
Auth endpoints — Login, Logout, Refresh Token.
Security:
- Rate limiting pada /login (OWASP A07)
- Brute-force lockout setelah 5 gagal
- JWT access token (15 menit) + refresh token (7 hari)
- Logout merevoke token via Redis blacklist
- Tidak pernah reveal apakah username atau password yang salah (generic error)
"""
from datetime import datetime, timezone
from flask import request, jsonify
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt,
)
from . import api_v1
from ...extensions import db, limiter
from ...models.account import Account
from ...utils.token_store import revoke_token
from ...utils.audit import log_action


@api_v1.post("/auth/login")
@limiter.limit("10 per minute")   # OWASP A07 — brute-force protection
def login():
    data = request.get_json(silent=True) or {}
    username = str(data.get("username", "")).strip()
    password = str(data.get("password", ""))

    # Validasi input dasar
    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    account = Account.query.filter_by(username=username, deleted_at=None).first()

    # Generic error — jangan beri tahu apakah username atau password yang salah
    INVALID_MSG = "Invalid credentials"

    if not account or not account.is_active:
        return jsonify({"error": INVALID_MSG}), 401

    if account.is_locked:
        return jsonify({"error": "Account is locked. Contact administrator."}), 403

    if not account.check_password(password):
        account.increment_failed_login(
            max_attempts=5
        )
        db.session.commit()
        log_action(None, "LOGIN_FAILED", "auth", account.id)
        db.session.commit()
        return jsonify({"error": INVALID_MSG}), 401

    # Login berhasil
    account.reset_failed_login()
    account.last_login_at = datetime.now(timezone.utc)
    account.last_login_ip = request.remote_addr
    db.session.commit()

    access_token  = create_access_token(identity=str(account.id))
    refresh_token = create_refresh_token(identity=str(account.id))

    log_action(account.id, "LOGIN", "auth")
    db.session.commit()

    return jsonify({
        "access_token":  access_token,
        "refresh_token": refresh_token,
        "user": {
            "id":          account.id,
            "username":    account.username,
            "full_name":   account.full_name,
            "role":        account.role.name,
            "permissions": [p.name for p in account.role.permissions],
        },
    }), 200


@api_v1.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    account_id   = get_jwt_identity()
    access_token = create_access_token(identity=account_id)  # sudah string
    return jsonify({"access_token": access_token}), 200


@api_v1.post("/auth/logout")
@jwt_required()
def logout():
    jti        = get_jwt()["jti"]
    account_id = get_jwt_identity()  # string — hanya untuk audit log

    # Revoke token di Redis
    from flask import current_app
    expires = int(current_app.config["JWT_ACCESS_TOKEN_EXPIRES"].total_seconds())
    revoke_token(jti, expires)

    log_action(account_id, "LOGOUT", "auth")
    db.session.commit()

    return jsonify({"message": "Logged out successfully"}), 200


@api_v1.get("/auth/me")
@jwt_required()
def me():
    account_id = int(get_jwt_identity())
    account    = Account.query.get_or_404(account_id)
    return jsonify({
        "id":        account.id,
        "username":  account.username,
        "email":     account.email,
        "full_name": account.full_name,
        "role":      account.role.name,
        "permissions": [p.name for p in account.role.permissions],
    }), 200
