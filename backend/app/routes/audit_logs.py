"""Audit logs blueprint (Administrator read-only)."""
from flask import Blueprint, jsonify, request

from app.models import AuditLog
from sqlalchemy import or_
from app.utils.decorators import admin_only
from app.utils.pagination import paginate

bp = Blueprint('audit_logs', __name__, url_prefix='/api/audit-logs')


@bp.route('', methods=['GET'])
@admin_only
def list_audit_logs():
    query = AuditLog.query
    if request.args.get('action'):
        query = query.filter_by(action=request.args.get('action'))
    if request.args.get('status'):
        query = query.filter_by(status=request.args.get('status'))
    search = (request.args.get('search') or '').strip()
    if search:
        pattern = f'%{search}%'
        query = query.filter(or_(AuditLog.action.like(pattern), AuditLog.resource_type.like(pattern), AuditLog.resource_id.like(pattern)))
    rows = query.order_by(AuditLog.created_at.desc())
    return jsonify(paginate(rows, max_per_page=100))
