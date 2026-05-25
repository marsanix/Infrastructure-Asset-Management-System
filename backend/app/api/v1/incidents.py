"""
Incident Management CRUD.

Security:
- State machine validation — transisi status divalidasi server (Business Logic)
- RBAC per endpoint
- Explicit serializer — tidak expose internal fields
- Audit log setiap perubahan status
- Pagination max 100
"""
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError

from . import api_v1
from ...extensions import db
from ...models.itsm import Incident, IncidentStatus, IncidentPriority, IncidentSeverity
from ...utils.rbac import require_permission
from ...utils.audit import log_action
from ...utils.state_machine import INCIDENT_TRANSITIONS, validate_transition
from flask import request, jsonify
from ...utils.rbac import get_current_account_id


class IncidentSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title           = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description     = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    priority        = fields.Str(load_default='Medium',
                                  validate=validate.OneOf([p.value for p in IncidentPriority]))
    severity        = fields.Str(load_default='S3',
                                  validate=validate.OneOf([s.value for s in IncidentSeverity]))
    status          = fields.Str(load_default='Open',
                                  validate=validate.OneOf([s.value for s in IncidentStatus]))
    asset_id        = fields.Int(load_default=None, allow_none=True)
    assigned_to     = fields.Int(load_default=None, allow_none=True)
    resolution_note = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _next_number() -> str:
    """Generate nomor incident: INC-YYYY-NNNN."""
    from ...models.itsm import Incident as Inc
    year  = datetime.now().year
    count = Inc.query.filter(
        db.extract('year', Inc.created_at) == year
    ).count()
    return f'INC-{year}-{count + 1:04d}'


def _serialize(i: Incident) -> dict:
    return {
        'id':              i.id,
        'incident_number': i.incident_number,
        'title':           i.title,
        'description':     i.description,
        'priority':        i.priority.value,
        'severity':        i.severity.value,
        'status':          i.status.value,
        'asset_id':        i.asset_id,
        'reported_by':     i.reported_by,
        'assigned_to':     i.assigned_to,
        'resolved_by':     i.resolved_by,
        'reported_at':     i.reported_at.isoformat() if i.reported_at else None,
        'resolved_at':     i.resolved_at.isoformat() if i.resolved_at else None,
        'closed_at':       i.closed_at.isoformat()   if i.closed_at   else None,
        'resolution_note': i.resolution_note,
        'created_at':      i.created_at.isoformat(),
        'updated_at':      i.updated_at.isoformat(),
    }


_schema = IncidentSchema()
UPDATABLE = {'title', 'description', 'priority', 'severity', 'status',
             'asset_id', 'assigned_to', 'resolution_note'}


@api_v1.get('/incidents')
@require_permission('incident:read')
def list_incidents():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    status   = request.args.get('status', '').strip()
    priority = request.args.get('priority', '').strip()
    search   = request.args.get('search', '').strip()[:100]

    query = Incident.query.filter(Incident.deleted_at.is_(None))

    if status:
        valid = [s.value for s in IncidentStatus]
        if status not in valid:
            return jsonify({'error': f'Invalid status. Must be one of: {valid}'}), 400
        query = query.filter(Incident.status == status)

    if priority:
        valid = [p.value for p in IncidentPriority]
        if priority not in valid:
            return jsonify({'error': f'Invalid priority. Must be one of: {valid}'}), 400
        query = query.filter(Incident.priority == priority)

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(Incident.title.ilike(like), Incident.incident_number.ilike(like))
        )

    pagination = query.order_by(Incident.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data':     [_serialize(i) for i in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/incidents/<int:incident_id>')
@require_permission('incident:read')
def get_incident(incident_id: int):
    inc = Incident.query.filter_by(id=incident_id, deleted_at=None).first()
    if not inc:
        return jsonify({'error': 'Incident not found'}), 404
    return jsonify(_serialize(inc)), 200


@api_v1.post('/incidents')
@require_permission('incident:create')
def create_incident():
    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    inc = Incident(
        incident_number = _next_number(),
        reported_by     = account_id,
        **{k: v for k, v in data.items() if k in UPDATABLE},
    )
    db.session.add(inc)
    db.session.flush()
    log_action(account_id, 'CREATE', 'incident', inc.id, new_data=_serialize(inc))
    db.session.commit()
    return jsonify(_serialize(inc)), 201


@api_v1.put('/incidents/<int:incident_id>')
@require_permission('incident:update')
def update_incident(incident_id: int):
    inc = Incident.query.filter_by(id=incident_id, deleted_at=None).first()
    if not inc:
        return jsonify({'error': 'Incident not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    data = {k: v for k, v in data.items() if k in UPDATABLE}
    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    # ── State machine validation ──────────────────────────────
    if 'status' in data and data['status'] != inc.status.value:
        ok, msg = validate_transition(INCIDENT_TRANSITIONS, inc.status.value, data['status'])
        if not ok:
            return jsonify({'error': msg}), 422

    old_data   = _serialize(inc)
    account_id = get_current_account_id()
    now        = datetime.now(timezone.utc)

    for key, value in data.items():
        setattr(inc, key, value)

    # Auto-set timestamps berdasarkan status
    if 'status' in data:
        if data['status'] == 'Resolved' and not inc.resolved_at:
            inc.resolved_at = now
            inc.resolved_by = account_id
        elif data['status'] == 'Closed' and not inc.closed_at:
            inc.closed_at = now

    log_action(account_id, 'UPDATE', 'incident', inc.id,
               old_data=old_data, new_data=_serialize(inc))
    db.session.commit()
    return jsonify(_serialize(inc)), 200


@api_v1.delete('/incidents/<int:incident_id>')
@require_permission('incident:delete')
def delete_incident(incident_id: int):
    inc = Incident.query.filter_by(id=incident_id, deleted_at=None).first()
    if not inc:
        return jsonify({'error': 'Incident not found'}), 404

    account_id    = get_jwt_identity()
    inc.deleted_at = datetime.now(timezone.utc)
    log_action(account_id, 'DELETE', 'incident', inc.id, old_data=_serialize(inc))
    db.session.commit()
    return jsonify({'message': 'Incident deleted'}), 200
