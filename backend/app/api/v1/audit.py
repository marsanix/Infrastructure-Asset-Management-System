"""
Audit Log endpoint — READ ONLY.

Security:
- Tidak ada endpoint POST/PUT/DELETE — audit log harus immutable
- Hanya Administrator yang bisa akses (permission audit:read)
- Sensitive fields di-mask dari response (password_hash tidak akan ada
  karena serializer account sudah exclude, tapi kita tambah filter defensif)
- Pagination ketat max 200
"""
from flask import request, jsonify
from . import api_v1
from ...models.audit_log import AuditLog
from ...utils.rbac import require_permission
from ...extensions import db

# Field yang tidak boleh muncul di old_data/new_data audit log
_SENSITIVE_KEYS = {'password_hash', 'password', 'token', 'secret', 'key'}


def _mask_sensitive(data: dict | None) -> dict | None:
    """Hapus field sensitif dari snapshot data audit log."""
    if not data:
        return data
    return {
        k: '***REDACTED***' if k.lower() in _SENSITIVE_KEYS else v
        for k, v in data.items()
    }


def _serialize(log: AuditLog) -> dict:
    return {
        'id':         log.id,
        'account_id': log.account_id,
        'action':     log.action,
        'module':     log.module,
        'record_id':  log.record_id,
        'old_data':   _mask_sensitive(log.old_data),
        'new_data':   _mask_sensitive(log.new_data),
        'ip_address': log.ip_address,
        # user_agent di-truncate untuk keamanan
        'user_agent': (log.user_agent or '')[:200] if log.user_agent else None,
        'created_at': log.created_at.isoformat(),
    }


@api_v1.get('/audit-logs')
@require_permission('audit:read')
def list_audit_logs():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 50))), 200)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    module     = request.args.get('module', '').strip()[:50]
    action     = request.args.get('action', '').strip()[:50]
    account_id = request.args.get('account_id', type=int)

    query = AuditLog.query

    if module:
        query = query.filter(AuditLog.module == module)
    if action:
        query = query.filter(AuditLog.action == action)
    if account_id:
        query = query.filter(AuditLog.account_id == account_id)

    pagination = query.order_by(AuditLog.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data':     [_serialize(log) for log in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/audit-logs/<int:log_id>')
@require_permission('audit:read')
def get_audit_log(log_id: int):
    log = AuditLog.query.get(log_id)
    if not log:
        return jsonify({'error': 'Audit log not found'}), 404
    return jsonify(_serialize(log)), 200
