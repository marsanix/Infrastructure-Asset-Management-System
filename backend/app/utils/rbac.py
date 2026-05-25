"""
RBAC decorator — cek permission sebelum eksekusi endpoint.
Contoh penggunaan:
    @require_permission("asset:create")
    def create_asset(): ...
"""
from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request
from ..models.account import Account


def get_current_account_id() -> int:
    """Helper: ambil account_id dari JWT sebagai integer."""
    return int(get_jwt_identity())


def require_permission(permission_name: str):
    """Decorator: pastikan user punya permission tertentu."""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            account_id = int(get_jwt_identity())   # JWT identity adalah string sejak v4.7
            account = Account.query.get(account_id)

            if not account or not account.is_active or account.is_deleted:
                return jsonify({"error": "Account not found or inactive"}), 401

            if not account.role.has_permission(permission_name):
                return jsonify({"error": "Forbidden — insufficient permissions"}), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator
