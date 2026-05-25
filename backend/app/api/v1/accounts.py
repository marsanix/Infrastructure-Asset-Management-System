"""
Account Management (Admin only).

Security:
- password_hash TIDAK PERNAH masuk ke response (Excessive Data Exposure)
- Password reset menggunakan bcrypt hash baru
- Hanya Administrator yang bisa create/update/delete account
- Self-update diizinkan untuk field terbatas (full_name, email)
- Tidak bisa deactivate diri sendiri
- Audit log setiap perubahan
"""
from datetime import datetime, timezone
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError, validates
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.account import Account
from ...models.role import Role
from ...utils.rbac import require_permission
from ...utils.audit import log_action


# ── Schemas ───────────────────────────────────────────────────

class AccountCreateSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    username  = fields.Str(required=True,
                            validate=[validate.Length(min=3, max=50),
                                      validate.Regexp(r'^[A-Za-z0-9_\.]+$',
                                                      error='Only alphanumeric, underscore, dot')])
    email     = fields.Email(required=True)
    password  = fields.Str(required=True, validate=validate.Length(min=8, max=128),
                            load_only=True)   # load_only: tidak pernah di-dump
    full_name = fields.Str(required=True, validate=validate.Length(min=1, max=150))
    role_id   = fields.Int(required=True, validate=validate.Range(min=1))
    is_active = fields.Bool(load_default=True)

    @validates('password')
    def validate_password_strength(self, value):
        """Minimal: 1 huruf besar, 1 angka, 1 karakter spesial."""
        import re
        if not re.search(r'[A-Z]', value):
            raise validate.ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', value):
            raise validate.ValidationError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise validate.ValidationError('Password must contain at least one special character')

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class AccountUpdateSchema(Schema):
    """Update schema — password tidak bisa diubah via endpoint ini."""
    class Meta:
        unknown = EXCLUDE

    email     = fields.Email()
    full_name = fields.Str(validate=validate.Length(min=1, max=150))
    role_id   = fields.Int(validate=validate.Range(min=1))
    is_active = fields.Bool()

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


class PasswordResetSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    new_password = fields.Str(required=True, validate=validate.Length(min=8, max=128),
                               load_only=True)

    @validates('new_password')
    def validate_strength(self, value):
        import re
        if not re.search(r'[A-Z]', value):
            raise validate.ValidationError('Password must contain at least one uppercase letter')
        if not re.search(r'\d', value):
            raise validate.ValidationError('Password must contain at least one digit')
        if not re.search(r'[^A-Za-z0-9]', value):
            raise validate.ValidationError('Password must contain at least one special character')


# ── Serializer — TIDAK PERNAH expose password_hash ───────────

def _serialize(a: Account) -> dict:
    """Explicit serializer — password_hash dikecualikan."""
    return {
        'id':                  a.id,
        'username':            a.username,
        'email':               a.email,
        'full_name':           a.full_name,
        'role_id':             a.role_id,
        'role_name':           a.role.name if a.role else None,
        'is_active':           a.is_active,
        'is_locked':           a.is_locked,
        'last_login_at':       a.last_login_at.isoformat() if a.last_login_at else None,
        'password_changed_at': a.password_changed_at.isoformat() if a.password_changed_at else None,
        'created_at':          a.created_at.isoformat(),
        'updated_at':          a.updated_at.isoformat(),
        # TIDAK ADA: password_hash, failed_login_count, last_login_ip
    }


create_schema   = AccountCreateSchema()
update_schema   = AccountUpdateSchema()
pw_reset_schema = PasswordResetSchema()
UPDATABLE       = {'email', 'full_name', 'role_id', 'is_active'}


# ── Endpoints ─────────────────────────────────────────────────

@api_v1.get('/accounts')
@require_permission('account:read')
def list_accounts():
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    search = request.args.get('search', '').strip()[:100]
    query  = Account.query.filter(Account.deleted_at.is_(None))

    if search:
        like = f'%{search}%'
        query = query.filter(
            db.or_(Account.username.ilike(like), Account.full_name.ilike(like),
                   Account.email.ilike(like))
        )

    pagination = query.order_by(Account.username).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify({
        'data':     [_serialize(a) for a in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


@api_v1.get('/accounts/<int:account_id>')
@require_permission('account:read')
def get_account(account_id: int):
    acc = Account.query.filter_by(id=account_id, deleted_at=None).first()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404
    return jsonify(_serialize(acc)), 200


@api_v1.post('/accounts')
@require_permission('account:create')
def create_account():
    try:
        data = create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    # Cek duplikat username dan email
    if Account.query.filter_by(username=data['username'], deleted_at=None).first():
        return jsonify({'error': 'Username already exists'}), 409
    if Account.query.filter_by(email=data['email'], deleted_at=None).first():
        return jsonify({'error': 'Email already exists'}), 409

    # Validasi role exists
    if not Role.query.get(data['role_id']):
        return jsonify({'error': 'Role not found'}), 422

    account_id = get_current_account_id()
    acc = Account(
        username  = data['username'],
        email     = data['email'],
        full_name = data['full_name'],
        role_id   = data['role_id'],
        is_active = data.get('is_active', True),
    )
    acc.set_password(data['password'])  # bcrypt hash

    db.session.add(acc)
    db.session.flush()
    log_action(account_id, 'CREATE', 'account', acc.id, new_data=_serialize(acc))
    db.session.commit()
    return jsonify(_serialize(acc)), 201


@api_v1.put('/accounts/<int:account_id>')
@require_permission('account:update')
def update_account(account_id: int):
    acc = Account.query.filter_by(id=account_id, deleted_at=None).first()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404

    try:
        data = update_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    data = {k: v for k, v in data.items() if k in UPDATABLE}
    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    current_account_id = get_current_account_id()

    # Tidak bisa deactivate diri sendiri
    if 'is_active' in data and not data['is_active'] and account_id == current_account_id:
        return jsonify({'error': 'Cannot deactivate your own account'}), 403

    # Cek duplikat email jika diubah
    if 'email' in data and data['email'] != acc.email:
        if Account.query.filter(
            Account.email == data['email'],
            Account.id != account_id,
            Account.deleted_at.is_(None)
        ).first():
            return jsonify({'error': 'Email already exists'}), 409

    old_data = _serialize(acc)
    for key, value in data.items():
        setattr(acc, key, value)

    log_action(current_account_id, 'UPDATE', 'account', acc.id,
               old_data=old_data, new_data=_serialize(acc))
    db.session.commit()
    return jsonify(_serialize(acc)), 200


@api_v1.post('/accounts/<int:account_id>/reset-password')
@require_permission('account:update')
def reset_password(account_id: int):
    """Reset password oleh admin — tidak perlu password lama."""
    acc = Account.query.filter_by(id=account_id, deleted_at=None).first()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404

    try:
        data = pw_reset_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    current_account_id = get_current_account_id()
    acc.set_password(data['new_password'])
    acc.password_changed_at = datetime.now(timezone.utc)
    acc.reset_failed_login()  # unlock jika terkunci

    log_action(current_account_id, 'PASSWORD_RESET', 'account', acc.id)
    db.session.commit()
    return jsonify({'message': 'Password reset successfully'}), 200


@api_v1.post('/accounts/<int:account_id>/unlock')
@require_permission('account:update')
def unlock_account(account_id: int):
    """Unlock akun yang terkunci karena brute-force."""
    acc = Account.query.filter_by(id=account_id, deleted_at=None).first()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404

    current_account_id = get_current_account_id()
    acc.reset_failed_login()
    log_action(current_account_id, 'UNLOCK', 'account', acc.id)
    db.session.commit()
    return jsonify({'message': 'Account unlocked'}), 200


@api_v1.delete('/accounts/<int:account_id>')
@require_permission('account:delete')
def delete_account(account_id: int):
    acc = Account.query.filter_by(id=account_id, deleted_at=None).first()
    if not acc:
        return jsonify({'error': 'Account not found'}), 404

    current_account_id = get_current_account_id()

    # Tidak bisa hapus diri sendiri
    if account_id == current_account_id:
        return jsonify({'error': 'Cannot delete your own account'}), 403

    old_data      = _serialize(acc)
    acc.deleted_at = datetime.now(timezone.utc)
    acc.is_active  = False
    log_action(current_account_id, 'DELETE', 'account', acc.id, old_data=old_data)
    db.session.commit()
    return jsonify({'message': 'Account deleted'}), 200
