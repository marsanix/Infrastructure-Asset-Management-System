"""Problem Management CRUD dengan state machine validation."""
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.itsm import Problem, ProblemStatus
from ...utils.rbac import require_permission
from ...utils.audit import log_action
from ...utils.state_machine import PROBLEM_TRANSITIONS, validate_transition


class ProblemSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    title       = fields.Str(required=True, validate=validate.Length(min=1, max=200))
    description = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    root_cause  = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    workaround  = fields.Str(load_default=None, validate=validate.Length(max=5000), allow_none=True)
    status      = fields.Str(load_default='Open',
                              validate=validate.OneOf([s.value for s in ProblemStatus]))
    asset_id    = fields.Int(load_default=None, allow_none=True)
    assigned_to = fields.Int(load_default=None, allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _next_number() -> str:
    year  = datetime.now().year
    count = Problem.query.filter(db.extract('year', Problem.created_at) == year).count()
    return f'PRB-{year}-{count + 1:04d}'


def _serialize(p: Problem) -> dict:
    return {
        'id':             p.id,
        'problem_number': p.problem_number,
        'title':          p.title,
        'description':    p.description,
        'root_cause':     p.root_cause,
        'workaround':     p.workaround,
        'status':         p.status.value,
        'asset_id':       p.asset_id,
        'reported_by':    p.reported_by,
        'assigned_to':    p.assigned_to,
        'resolved_by':    p.resolved_by,
        'resolved_at':    p.resolved_at.isoformat() if p.resolved_at else None,
        'created_at':     p.created_at.isoformat(),
        'updated_at':     p.updated_at.isoformat(),
    }


_schema   = ProblemSchema()
UPDATABLE = {'title', 'description', 'root_cause', 'workaround', 'status', 'asset_id', 'assigned_to'}


@api_v1.get('/problems')
@require_permission('problem:read')
def list_problems():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    status = request.args.get('status', '').strip()
    search = request.args.get('search', '').strip()[:100]
    query  = Problem.query.filter(Problem.deleted_at.is_(None))

    if status:
        valid = [s.value for s in ProblemStatus]
        if status not in valid:
            return jsonify({'error': f'Invalid status. Must be one of: {valid}'}), 400
        query = query.filter(Problem.status == status)

    if search:
        like = f'%{search}%'
        query = query.filter(db.or_(Problem.title.ilike(like), Problem.problem_number.ilike(like)))

    pagination = query.order_by(Problem.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data':     [_serialize(p) for p in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/problems/<int:problem_id>')
@require_permission('problem:read')
def get_problem(problem_id: int):
    prb = Problem.query.filter_by(id=problem_id, deleted_at=None).first()
    if not prb:
        return jsonify({'error': 'Problem not found'}), 404
    return jsonify(_serialize(prb)), 200


@api_v1.post('/problems')
@require_permission('problem:create')
def create_problem():
    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    prb = Problem(
        problem_number = _next_number(),
        reported_by    = account_id,
        **{k: v for k, v in data.items() if k in UPDATABLE},
    )
    db.session.add(prb)
    db.session.flush()
    log_action(account_id, 'CREATE', 'problem', prb.id, new_data=_serialize(prb))
    db.session.commit()
    return jsonify(_serialize(prb)), 201


@api_v1.put('/problems/<int:problem_id>')
@require_permission('problem:update')
def update_problem(problem_id: int):
    prb = Problem.query.filter_by(id=problem_id, deleted_at=None).first()
    if not prb:
        return jsonify({'error': 'Problem not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    data = {k: v for k, v in data.items() if k in UPDATABLE}
    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    if 'status' in data and data['status'] != prb.status.value:
        ok, msg = validate_transition(PROBLEM_TRANSITIONS, prb.status.value, data['status'])
        if not ok:
            return jsonify({'error': msg}), 422

    old_data   = _serialize(prb)
    account_id = get_current_account_id()

    for key, value in data.items():
        setattr(prb, key, value)

    if 'status' in data and data['status'] == 'Resolved' and not prb.resolved_at:
        prb.resolved_at = datetime.now(timezone.utc)
        prb.resolved_by = account_id

    log_action(account_id, 'UPDATE', 'problem', prb.id,
               old_data=old_data, new_data=_serialize(prb))
    db.session.commit()
    return jsonify(_serialize(prb)), 200


@api_v1.delete('/problems/<int:problem_id>')
@require_permission('problem:delete')
def delete_problem(problem_id: int):
    prb = Problem.query.filter_by(id=problem_id, deleted_at=None).first()
    if not prb:
        return jsonify({'error': 'Problem not found'}), 404
    account_id     = get_jwt_identity()
    prb.deleted_at = datetime.now(timezone.utc)
    log_action(account_id, 'DELETE', 'problem', prb.id, old_data=_serialize(prb))
    db.session.commit()
    return jsonify({'message': 'Problem deleted'}), 200
