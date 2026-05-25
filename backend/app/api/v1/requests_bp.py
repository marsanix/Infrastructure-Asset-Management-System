"""Request Management CRUD dengan state machine validation."""
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.itsm import Request, RequestStatus, RequestPriority, RequestType
from ...utils.rbac import require_permission
from ...utils.audit import log_action
from ...utils.state_machine import REQUEST_TRANSITIONS, validate_transition


class RequestSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title        = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description  = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    request_type = fields.Str(load_default='Other',
                               validate=validate.OneOf([t.value for t in RequestType]))
    priority     = fields.Str(load_default='Medium',
                               validate=validate.OneOf([p.value for p in RequestPriority]))
    status       = fields.Str(load_default='Draft',
                               validate=validate.OneOf([s.value for s in RequestStatus]))
    asset_id     = fields.Int(load_default=None, allow_none=True)
    notes        = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _next_number() -> str:
    year  = datetime.now().year
    count = Request.query.filter(db.extract('year', Request.created_at) == year).count()
    return f'REQ-{year}-{count + 1:04d}'


def _serialize(r: Request) -> dict:
    return {
        'id':             r.id,
        'request_number': r.request_number,
        'title':          r.title,
        'description':    r.description,
        'request_type':   r.request_type.value,
        'priority':       r.priority.value,
        'status':         r.status.value,
        'asset_id':       r.asset_id,
        'requested_by':   r.requested_by,
        'approved_by':    r.approved_by,
        'fulfilled_by':   r.fulfilled_by,
        'approved_at':    r.approved_at.isoformat()  if r.approved_at  else None,
        'fulfilled_at':   r.fulfilled_at.isoformat() if r.fulfilled_at else None,
        'notes':          r.notes,
        'created_at':     r.created_at.isoformat(),
        'updated_at':     r.updated_at.isoformat(),
    }


_schema   = RequestSchema()
UPDATABLE = {'title', 'description', 'request_type', 'priority', 'status', 'asset_id', 'notes'}


@api_v1.get('/requests')
@require_permission('request:read')
def list_requests():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()[:100]
    query  = Request.query.filter(Request.deleted_at.is_(None))

    if status:
        valid = [s.value for s in RequestStatus]
        if status not in valid:
            return jsonify({'error': f'Invalid status. Must be one of: {valid}'}), 400
        query = query.filter(Request.status == status)

    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(Request.title.ilike(like), Request.request_number.ilike(like)))

    pagination = query.order_by(Request.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data':     [_serialize(r) for r in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/requests/<int:request_id>')
@require_permission('request:read')
def get_request(request_id: int):
    req = Request.query.filter_by(id=request_id, deleted_at=None).first()
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    return jsonify(_serialize(req)), 200


@api_v1.post('/requests')
@require_permission('request:create')
def create_request():
    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    req = Request(
        request_number = _next_number(),
        requested_by   = account_id,
        **{k: v for k, v in data.items() if k in UPDATABLE},
    )
    db.session.add(req)
    db.session.flush()
    log_action(account_id, 'CREATE', 'request', req.id, new_data=_serialize(req))
    db.session.commit()
    return jsonify(_serialize(req)), 201


@api_v1.put('/requests/<int:request_id>')
@require_permission('request:update')
def update_request(request_id: int):
    req = Request.query.filter_by(id=request_id, deleted_at=None).first()
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    data = {k: v for k, v in data.items() if k in UPDATABLE}
    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    if 'status' in data and data['status'] != req.status.value:
        ok, msg = validate_transition(REQUEST_TRANSITIONS, req.status.value, data['status'])
        if not ok:
            return jsonify({'error': msg}), 422

    old_data   = _serialize(req)
    account_id = get_current_account_id()
    now        = datetime.now(timezone.utc)

    for key, value in data.items():
        setattr(req, key, value)

    if 'status' in data:
        if data['status'] == 'Approved' and not req.approved_at:
            req.approved_at = now
            req.approved_by = account_id
        elif data['status'] == 'Completed' and not req.fulfilled_at:
            req.fulfilled_at = now
            req.fulfilled_by = account_id

    log_action(account_id, 'UPDATE', 'request', req.id,
               old_data=old_data, new_data=_serialize(req))
    db.session.commit()
    return jsonify(_serialize(req)), 200


@api_v1.delete('/requests/<int:request_id>')
@require_permission('request:delete')
def delete_request(request_id: int):
    req = Request.query.filter_by(id=request_id, deleted_at=None).first()
    if not req:
        return jsonify({'error': 'Request not found'}), 404
    account_id     = get_jwt_identity()
    req.deleted_at = datetime.now(timezone.utc)
    log_action(account_id, 'DELETE', 'request', req.id, old_data=_serialize(req))
    db.session.commit()
    return jsonify({'message': 'Request deleted'}), 200
