"""Change Management CRUD dengan state machine validation."""
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.itsm import Change, ChangeStatus, ChangePriority, ChangeType
from ...utils.rbac import require_permission
from ...utils.audit import log_action
from ...utils.state_machine import CHANGE_TRANSITIONS, validate_transition


class ChangeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title         = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description   = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    change_type   = fields.Str(load_default='Normal',
                                validate=validate.OneOf([t.value for t in ChangeType]))
    priority      = fields.Str(load_default='Medium',
                                validate=validate.OneOf([p.value for p in ChangePriority]))
    status        = fields.Str(load_default='Draft',
                                validate=validate.OneOf([s.value for s in ChangeStatus]))
    asset_id      = fields.Int(load_default=None, allow_none=True)
    planned_start = fields.DateTime(load_default=None, allow_none=True)
    planned_end   = fields.DateTime(load_default=None, allow_none=True)
    rollback_plan = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    notes         = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _next_number() -> str:
    year  = datetime.now().year
    count = Change.query.filter(db.extract('year', Change.created_at) == year).count()
    return f'CHG-{year}-{count + 1:04d}'


def _serialize(c: Change) -> dict:
    return {
        'id':             c.id,
        'change_number':  c.change_number,
        'title':          c.title,
        'description':    c.description,
        'change_type':    c.change_type.value,
        'priority':       c.priority.value,
        'status':         c.status.value,
        'asset_id':       c.asset_id,
        'requested_by':   c.requested_by,
        'approved_by':    c.approved_by,
        'planned_start':  c.planned_start.isoformat() if c.planned_start else None,
        'planned_end':    c.planned_end.isoformat()   if c.planned_end   else None,
        'actual_start':   c.actual_start.isoformat()  if c.actual_start  else None,
        'actual_end':     c.actual_end.isoformat()    if c.actual_end    else None,
        'rollback_plan':  c.rollback_plan,
        'notes':          c.notes,
        'created_at':     c.created_at.isoformat(),
        'updated_at':     c.updated_at.isoformat(),
    }


_schema    = ChangeSchema()
UPDATABLE  = {'title', 'description', 'change_type', 'priority', 'status',
              'asset_id', 'planned_start', 'planned_end', 'rollback_plan', 'notes'}


@api_v1.get('/changes')
@require_permission('change:read')
def list_changes():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()[:100]
    query  = Change.query.filter(Change.deleted_at.is_(None))

    if status:
        valid = [s.value for s in ChangeStatus]
        if status not in valid:
            return jsonify({'error': f'Invalid status. Must be one of: {valid}'}), 400
        query = query.filter(Change.status == status)

    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(Change.title.ilike(like), Change.change_number.ilike(like)))

    pagination = query.order_by(Change.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data':     [_serialize(c) for c in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/changes/<int:change_id>')
@require_permission('change:read')
def get_change(change_id: int):
    chg = Change.query.filter_by(id=change_id, deleted_at=None).first()
    if not chg:
        return jsonify({'error': 'Change not found'}), 404
    return jsonify(_serialize(chg)), 200


@api_v1.post('/changes')
@require_permission('change:create')
def create_change():
    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    chg = Change(
        change_number = _next_number(),
        requested_by  = account_id,
        **{k: v for k, v in data.items() if k in UPDATABLE},
    )
    db.session.add(chg)
    db.session.flush()
    log_action(account_id, 'CREATE', 'change', chg.id, new_data=_serialize(chg))
    db.session.commit()
    return jsonify(_serialize(chg)), 201


@api_v1.put('/changes/<int:change_id>')
@require_permission('change:update')
def update_change(change_id: int):
    chg = Change.query.filter_by(id=change_id, deleted_at=None).first()
    if not chg:
        return jsonify({'error': 'Change not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    data = {k: v for k, v in data.items() if k in UPDATABLE}
    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    # State machine validation
    if 'status' in data and data['status'] != chg.status.value:
        ok, msg = validate_transition(CHANGE_TRANSITIONS, chg.status.value, data['status'])
        if not ok:
            return jsonify({'error': msg}), 422

    old_data   = _serialize(chg)
    account_id = get_current_account_id()
    now        = datetime.now(timezone.utc)

    for key, value in data.items():
        setattr(chg, key, value)

    # Auto-set approved_by dan timestamps
    if 'status' in data:
        if data['status'] == 'Approved':
            chg.approved_by = account_id
        elif data['status'] == 'In Progress' and not chg.actual_start:
            chg.actual_start = now
        elif data['status'] == 'Completed' and not chg.actual_end:
            chg.actual_end = now

    log_action(account_id, 'UPDATE', 'change', chg.id,
               old_data=old_data, new_data=_serialize(chg))
    db.session.commit()
    return jsonify(_serialize(chg)), 200


@api_v1.delete('/changes/<int:change_id>')
@require_permission('change:delete')
def delete_change(change_id: int):
    chg = Change.query.filter_by(id=change_id, deleted_at=None).first()
    if not chg:
        return jsonify({'error': 'Change not found'}), 404
    account_id     = get_jwt_identity()
    chg.deleted_at = datetime.now(timezone.utc)
    log_action(account_id, 'DELETE', 'change', chg.id, old_data=_serialize(chg))
    db.session.commit()
    return jsonify({'message': 'Change deleted'}), 200
