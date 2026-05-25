"""
Asset Credentials endpoint — password perangkat (router, switch, firewall, AP, printer).

Security:
- Password disimpan terenkripsi AES-256 (Fernet) — TIDAK PERNAH plaintext di DB
- GET list: tidak expose password sama sekali (hanya metadata)
- GET detail: expose password hanya jika user punya permission credential:read
  dan request di-log ke audit
- Hanya Administrator yang bisa akses (permission credential:read/create/update/delete)
- Audit log setiap akses credential (termasuk READ)
"""
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.asset_credential import AssetCredential
from ...models.asset import Asset
from ...utils.rbac import require_permission
from ...utils.audit import log_action

CREDENTIAL_TYPES = ['SSH', 'Web Console', 'SNMP', 'Telnet', 'RDP', 'API Key', 'Other']


class CredentialSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    credential_type = fields.Str(required=True,
                                  validate=validate.OneOf(CREDENTIAL_TYPES))
    username        = fields.Str(load_default=None, validate=validate.Length(max=200), allow_none=True)
    password        = fields.Str(required=True, validate=validate.Length(min=1, max=500),
                                  load_only=True)   # load_only: tidak pernah di-dump
    notes           = fields.Str(load_default=None, validate=validate.Length(max=1000), allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize_safe(c: AssetCredential) -> dict:
    """Serializer TANPA password — untuk list endpoint."""
    return {
        'id':              c.id,
        'asset_id':        c.asset_id,
        'credential_type': c.credential_type,
        'username':        c.username,
        'notes':           c.notes,
        'created_by':      c.created_by,
        'created_at':      c.created_at.isoformat(),
        'updated_at':      c.updated_at.isoformat(),
        # password_encrypted TIDAK ADA di sini
    }


def _serialize_with_password(c: AssetCredential) -> dict:
    """Serializer DENGAN password — hanya untuk endpoint reveal yang di-audit."""
    base = _serialize_safe(c)
    try:
        base['password'] = c.get_password()
    except Exception:
        base['password'] = None  # decrypt gagal — key mungkin berubah
    return base


_schema = CredentialSchema()


@api_v1.get('/assets/<int:asset_id>/credentials')
@require_permission('credential:read')
def list_credentials(asset_id: int):
    """List credentials — TANPA password."""
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    creds = AssetCredential.query.filter_by(asset_id=asset_id).all()
    return jsonify({'data': [_serialize_safe(c) for c in creds]}), 200


@api_v1.get('/assets/<int:asset_id>/credentials/<int:cred_id>/reveal')
@require_permission('credential:read')
def reveal_credential(asset_id: int, cred_id: int):
    """
    Reveal password — endpoint terpisah yang selalu di-audit.
    Setiap akses ke password tercatat di audit log.
    """
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    cred = AssetCredential.query.filter_by(id=cred_id, asset_id=asset_id).first()
    if not cred:
        return jsonify({'error': 'Credential not found'}), 404

    account_id = get_current_account_id()
    # Audit setiap akses reveal — ini penting untuk compliance
    log_action(account_id, 'CREDENTIAL_REVEAL', 'credential', cred_id,
               new_data={'asset_id': asset_id, 'credential_type': cred.credential_type})
    db.session.commit()

    return jsonify(_serialize_with_password(cred)), 200


@api_v1.post('/assets/<int:asset_id>/credentials')
@require_permission('credential:create')
def create_credential(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    cred = AssetCredential(
        asset_id        = asset_id,
        credential_type = data['credential_type'],
        username        = data.get('username'),
        notes           = data.get('notes'),
        created_by      = account_id,
    )
    cred.set_password(data['password'])  # AES-256 encrypt

    db.session.add(cred)
    db.session.flush()
    # Audit log TANPA password
    log_action(account_id, 'CREATE', 'credential', cred.id,
               new_data=_serialize_safe(cred))
    db.session.commit()

    return jsonify(_serialize_safe(cred)), 201


@api_v1.put('/assets/<int:asset_id>/credentials/<int:cred_id>')
@require_permission('credential:update')
def update_credential(asset_id: int, cred_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    cred = AssetCredential.query.filter_by(id=cred_id, asset_id=asset_id).first()
    if not cred:
        return jsonify({'error': 'Credential not found'}), 404

    # Update schema — password opsional
    class UpdateSchema(Schema):
        class Meta:
            unknown = EXCLUDE
        credential_type = fields.Str(validate=validate.OneOf(CREDENTIAL_TYPES))
        username        = fields.Str(validate=validate.Length(max=200), allow_none=True)
        password        = fields.Str(validate=validate.Length(min=1, max=500), load_only=True)
        notes           = fields.Str(validate=validate.Length(max=1000), allow_none=True)

    try:
        data = UpdateSchema().load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    old_data   = _serialize_safe(cred)

    if 'credential_type' in data:
        cred.credential_type = data['credential_type']
    if 'username' in data:
        cred.username = data['username']
    if 'notes' in data:
        cred.notes = data['notes']
    if 'password' in data:
        cred.set_password(data['password'])

    log_action(account_id, 'UPDATE', 'credential', cred.id,
               old_data=old_data, new_data=_serialize_safe(cred))
    db.session.commit()
    return jsonify(_serialize_safe(cred)), 200


@api_v1.delete('/assets/<int:asset_id>/credentials/<int:cred_id>')
@require_permission('credential:delete')
def delete_credential(asset_id: int, cred_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    cred = AssetCredential.query.filter_by(id=cred_id, asset_id=asset_id).first()
    if not cred:
        return jsonify({'error': 'Credential not found'}), 404

    account_id = get_current_account_id()
    old_data   = _serialize_safe(cred)
    db.session.delete(cred)
    log_action(account_id, 'DELETE', 'credential', cred.id, old_data=old_data)
    db.session.commit()
    return jsonify({'message': 'Credential deleted'}), 200
