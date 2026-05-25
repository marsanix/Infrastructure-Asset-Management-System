"""
Audit logging helper.
Setiap CREATE / UPDATE / DELETE pada resource penting dicatat ke tabel audit_logs.
"""
from flask import Flask, request as flask_request
from ..extensions import db
from ..models.audit_log import AuditLog


def log_action(
    account_id: int | None,
    action: str,
    module: str,
    record_id: int | None = None,
    old_data: dict | None = None,
    new_data: dict | None = None,
) -> None:
    """Tulis satu baris audit log."""
    entry = AuditLog(
        account_id=account_id,
        action=action,
        module=module,
        record_id=record_id,
        old_data=old_data,
        new_data=new_data,
        ip_address=flask_request.remote_addr,
        user_agent=flask_request.headers.get("User-Agent", "")[:500],
    )
    db.session.add(entry)
    # Commit dilakukan bersama transaksi utama — jangan commit di sini


def register_audit_hooks(app: Flask) -> None:
    """Hook teardown — pastikan session di-close dengan benar."""
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        db.session.remove()
