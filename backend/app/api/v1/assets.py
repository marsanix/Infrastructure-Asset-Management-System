"""
Asset CRUD endpoints — lengkap dengan security hardening.

Security checklist per endpoint:
- RBAC via @require_permission (OWASP A01 / API1 Broken Access Control)
- Input validation via Marshmallow — unknown fields di-EXCLUDE (API3 Mass Assignment)
- Explicit allowlist field yang boleh diupdate (anti mass-assignment)
- Pagination dengan batas max per_page=100 (API4 Unrestricted Resource Consumption)
- Soft delete — data tidak hilang permanen
- Audit log setiap mutasi
- Query filter via SQLAlchemy ORM — tidak ada raw SQL (OWASP A03 Injection)
- Tidak ada stack trace di response production (OWASP A05)
"""
from datetime import datetime, timezone
from flask import request, jsonify, current_app
from ...utils.rbac import get_current_account_id
from marshmallow import Schema, fields, validate, ValidationError, EXCLUDE, pre_load
import re

from . import api_v1
from ...extensions import db
from ...models.asset import Asset, AssetStatus
from ...models.model_device import DeviceModel
from ...models.location import Location
from ...models.employee import Employee
from ...utils.rbac import require_permission
from ...utils.audit import log_action


# ── Marshmallow Schemas ───────────────────────────────────────

class AssetCreateSchema(Schema):
    """Schema untuk CREATE — semua field wajib/opsional didefinisikan eksplisit."""
    class Meta:
        unknown = EXCLUDE  # Buang field tidak dikenal — anti mass-assignment (API3)

    asset_tag       = fields.Str(required=True,
                                  validate=[validate.Length(min=1, max=50),
                                            validate.Regexp(r'^[A-Za-z0-9\-_]+$',
                                                            error='asset_tag: only alphanumeric, dash, underscore')])
    serial_number   = fields.Str(required=True,  validate=validate.Length(min=1, max=100))
    po_number       = fields.Str(load_default=None, validate=validate.Length(max=100))
    model_id        = fields.Int(required=True,  validate=validate.Range(min=1))
    location_id     = fields.Int(required=True,  validate=validate.Range(min=1))
    employee_id     = fields.Int(load_default=None, validate=validate.Range(min=1), allow_none=True)
    status          = fields.Str(load_default='Available',
                                  validate=validate.OneOf([s.value for s in AssetStatus]))
    purchase_date   = fields.Date(load_default=None, allow_none=True)
    warranty_months = fields.Int(load_default=None, validate=validate.Range(min=0, max=600), allow_none=True)
    os_license      = fields.Str(load_default=None, validate=validate.Length(max=100), allow_none=True)
    notes           = fields.Str(load_default=None, validate=validate.Length(max=2000), allow_none=True)

    @pre_load
    def strip_strings(self, data, **kwargs):
        """Strip whitespace dari semua string input."""
        return {
            k: v.strip() if isinstance(v, str) else v
            for k, v in data.items()
        }


class AssetUpdateSchema(AssetCreateSchema):
    """Schema untuk UPDATE — semua field opsional (partial update)."""
    asset_tag     = fields.Str(required=False, validate=[
        validate.Length(min=1, max=50),
        validate.Regexp(r'^[A-Za-z0-9\-_]+$'),
    ])
    serial_number = fields.Str(required=False, validate=validate.Length(min=1, max=100))
    model_id      = fields.Int(required=False, validate=validate.Range(min=1))
    location_id   = fields.Int(required=False, validate=validate.Range(min=1))


# Explicit allowlist field yang boleh diupdate (anti mass-assignment)
UPDATABLE_FIELDS = {
    'asset_tag', 'serial_number', 'po_number', 'model_id',
    'location_id', 'employee_id', 'status', 'purchase_date',
    'warranty_months', 'os_license', 'notes',
}

create_schema = AssetCreateSchema()
update_schema = AssetUpdateSchema()


# ── Serializer ────────────────────────────────────────────────

def _serialize(a: Asset) -> dict:
    """Serialisasi asset ke dict — hanya field yang aman untuk expose."""
    # SQLite menyimpan enum sebagai string (untuk testing), PostgreSQL sebagai enum object
    status_val = a.status.value if hasattr(a.status, 'value') else str(a.status)
    return {
        'id':              a.id,
        'asset_tag':       a.asset_tag,
        'serial_number':   a.serial_number,
        'po_number':       a.po_number,
        'model_id':        a.model_id,
        'location_id':     a.location_id,
        'employee_id':     a.employee_id,
        'status':          status_val,
        'purchase_date':   a.purchase_date.isoformat() if a.purchase_date else None,
        'warranty_months': a.warranty_months,
        'os_license':      a.os_license,
        'notes':           a.notes,
        'created_at':      a.created_at.isoformat(),
        'updated_at':      a.updated_at.isoformat(),
    }


def _serialize_detail(a: Asset) -> dict:
    """Serialisasi lengkap dengan relasi — untuk endpoint detail."""
    base = _serialize(a)
    base.update({
        'model': {
            'id':   a.model.id,
            'name': a.model.name,
            'brand': None,
            'category': None,
        } if a.model else None,
        'location': {
            'id':   a.location.id,
            'name': a.location.name,
        } if a.location else None,
        'employee': {
            'id':         a.employee.id,
            'name':       a.employee.name,
            'department': a.employee.department_id,
        } if a.employee else None,
        'network': {
            'ip_address':    str(a.network_detail.ip_address)  if a.network_detail and a.network_detail.ip_address  else None,
            'mac_address':   str(a.network_detail.mac_address) if a.network_detail and a.network_detail.mac_address else None,
            'hostname':      a.network_detail.hostname         if a.network_detail else None,
            'vlan':          a.network_detail.vlan             if a.network_detail else None,
        } if a.network_detail else None,
    })
    return base


# ── Helper: validasi FK exists ────────────────────────────────

def _validate_fk(data: dict) -> list[str]:
    """Cek foreign key references exist di DB sebelum insert/update."""
    errors = []
    if 'model_id' in data and data['model_id']:
        if not DeviceModel.query.filter_by(id=data['model_id'], deleted_at=None).first():
            errors.append(f"model_id {data['model_id']} not found")
    if 'location_id' in data and data['location_id']:
        if not Location.query.filter_by(id=data['location_id'], deleted_at=None).first():
            errors.append(f"location_id {data['location_id']} not found")
    if 'employee_id' in data and data['employee_id']:
        if not Employee.query.filter_by(id=data['employee_id'], deleted_at=None).first():
            errors.append(f"employee_id {data['employee_id']} not found")
    return errors


# ── GET /assets ───────────────────────────────────────────────

@api_v1.get('/assets')
@require_permission('asset:read')
def list_assets():
    # Sanitasi query params
    try:
        page     = max(1, int(request.args.get('page', 1)))
        per_page = min(max(1, int(request.args.get('per_page', 20))), 100)  # max 100
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid pagination parameters'}), 400

    status     = request.args.get('status', '').strip()
    search     = request.args.get('search', '').strip()
    category_id = request.args.get('category_id', type=int)
    location_id = request.args.get('location_id', type=int)

    query = Asset.query.filter_by(deleted_at=None)

    # Filter status — validasi enum
    if status:
        valid_statuses = [s.value for s in AssetStatus]
        if status not in valid_statuses:
            return jsonify({'error': f'Invalid status. Must be one of: {valid_statuses}'}), 400
        query = query.filter(Asset.status == status)

    # Search — via ORM, tidak ada raw SQL (OWASP A03)
    if search:
        like = f'%{search[:100]}%'  # batasi panjang search string
        query = query.filter(
            db.or_(
                Asset.asset_tag.ilike(like),
                Asset.serial_number.ilike(like),
                Asset.po_number.ilike(like),
            )
        )

    # Filter by location
    if location_id:
        query = query.filter(Asset.location_id == location_id)

    # Filter by category (via join)
    if category_id:
        query = query.join(DeviceModel).filter(DeviceModel.category_id == category_id)

    pagination = query.order_by(Asset.asset_tag).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return jsonify({
        'data':     [_serialize(a) for a in pagination.items],
        'total':    pagination.total,
        'page':     pagination.page,
        'per_page': pagination.per_page,
        'pages':    pagination.pages,
    }), 200


# ── GET /assets/<id> ──────────────────────────────────────────

@api_v1.get('/assets/<int:asset_id>')
@require_permission('asset:read')
def get_asset(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        # Jangan beda response antara "not found" dan "no permission" — BOLA prevention
        return jsonify({'error': 'Asset not found'}), 404
    return jsonify(_serialize_detail(asset)), 200


# ── POST /assets ──────────────────────────────────────────────

@api_v1.post('/assets')
@require_permission('asset:create')
def create_asset():
    try:
        data = create_schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    # Validasi FK
    fk_errors = _validate_fk(data)
    if fk_errors:
        return jsonify({'errors': fk_errors}), 422

    # Cek duplikat asset_tag dan serial_number
    if Asset.query.filter_by(asset_tag=data['asset_tag'], deleted_at=None).first():
        return jsonify({'error': 'asset_tag already exists'}), 409
    if Asset.query.filter_by(serial_number=data['serial_number'], deleted_at=None).first():
        return jsonify({'error': 'serial_number already exists'}), 409

    account_id = get_current_account_id()
    asset = Asset(**data, created_by=account_id)
    db.session.add(asset)
    db.session.flush()

    log_action(account_id, 'CREATE', 'asset', asset.id, new_data=_serialize(asset))
    db.session.commit()

    return jsonify(_serialize(asset)), 201


# ── PUT /assets/<id> ──────────────────────────────────────────

@api_v1.put('/assets/<int:asset_id>')
@require_permission('asset:update')
def update_asset(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    try:
        data = update_schema.load(request.get_json(silent=True) or {}, partial=True)
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    # Explicit allowlist — hanya update field yang diizinkan (anti mass-assignment)
    data = {k: v for k, v in data.items() if k in UPDATABLE_FIELDS}

    if not data:
        return jsonify({'error': 'No valid fields to update'}), 400

    # Validasi FK untuk field yang diupdate
    fk_errors = _validate_fk(data)
    if fk_errors:
        return jsonify({'errors': fk_errors}), 422

    # Cek duplikat jika asset_tag atau serial_number diubah
    if 'asset_tag' in data and data['asset_tag'] != asset.asset_tag:
        if Asset.query.filter(
            Asset.asset_tag == data['asset_tag'],
            Asset.id != asset_id,
            Asset.deleted_at.is_(None)
        ).first():
            return jsonify({'error': 'asset_tag already exists'}), 409

    if 'serial_number' in data and data['serial_number'] != asset.serial_number:
        if Asset.query.filter(
            Asset.serial_number == data['serial_number'],
            Asset.id != asset_id,
            Asset.deleted_at.is_(None)
        ).first():
            return jsonify({'error': 'serial_number already exists'}), 409

    old_data   = _serialize(asset)
    account_id = get_current_account_id()

    for key, value in data.items():
        setattr(asset, key, value)

    log_action(account_id, 'UPDATE', 'asset', asset.id,
               old_data=old_data, new_data=_serialize(asset))
    db.session.commit()

    return jsonify(_serialize_detail(asset)), 200


# ── DELETE /assets/<id> ───────────────────────────────────────

@api_v1.delete('/assets/<int:asset_id>')
@require_permission('asset:delete')
def delete_asset(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    old_data   = _serialize(asset)
    account_id = get_current_account_id()

    # Soft delete
    asset.deleted_at = datetime.now(timezone.utc)
    log_action(account_id, 'DELETE', 'asset', asset.id, old_data=old_data)
    db.session.commit()

    return jsonify({'message': 'Asset deleted successfully'}), 200


# ── GET /assets/<id>/history ──────────────────────────────────

@api_v1.get('/assets/<int:asset_id>/history')
@require_permission('asset:read')
def asset_history(asset_id: int):
    """Riwayat perubahan aset dari audit_log."""
    from ...models.audit_log import AuditLog

    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    logs = (AuditLog.query
            .filter_by(module='asset', record_id=asset_id)
            .order_by(AuditLog.created_at.desc())
            .limit(50)
            .all())

    return jsonify({
        'data': [
            {
                'id':         log.id,
                'action':     log.action,
                'account_id': log.account_id,
                'old_data':   log.old_data,
                'new_data':   log.new_data,
                'ip_address': log.ip_address,
                'created_at': log.created_at.isoformat(),
            }
            for log in logs
        ]
    }), 200
