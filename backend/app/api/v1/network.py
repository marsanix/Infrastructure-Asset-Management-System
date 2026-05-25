"""
Network Details endpoint — 1:1 dengan Asset.

Security:
- RBAC per endpoint
- IP/MAC address divalidasi format sebelum disimpan
- Tidak expose credential di response ini
- Audit log setiap perubahan
"""
import re
from marshmallow import Schema, fields, validate, EXCLUDE, pre_load, ValidationError, validates
from flask import request, jsonify
from ...utils.rbac import get_current_account_id

from . import api_v1
from ...extensions import db
from ...models.network_detail import NetworkDetail
from ...models.asset import Asset
from ...utils.rbac import require_permission
from ...utils.audit import log_action


# ── Validators ────────────────────────────────────────────────

IPV4_RE  = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
IPV6_RE  = re.compile(r'^[0-9a-fA-F:]+$')
MAC_RE   = re.compile(r'^([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2}$')


def _valid_ip(value: str) -> bool:
    if not value:
        return True
    if IPV4_RE.match(value):
        parts = value.split('.')
        return all(0 <= int(p) <= 255 for p in parts)
    return bool(IPV6_RE.match(value))


class NetworkSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    ip_address    = fields.Str(load_default=None, validate=validate.Length(max=45), allow_none=True)
    mac_address   = fields.Str(load_default=None, validate=validate.Length(max=17), allow_none=True)
    subnet_mask   = fields.Str(load_default=None, validate=validate.Length(max=45), allow_none=True)
    gateway       = fields.Str(load_default=None, validate=validate.Length(max=45), allow_none=True)
    dns_primary   = fields.Str(load_default=None, validate=validate.Length(max=45), allow_none=True)
    dns_secondary = fields.Str(load_default=None, validate=validate.Length(max=45), allow_none=True)
    vlan          = fields.Str(load_default=None, validate=validate.Length(max=20), allow_none=True)
    hostname      = fields.Str(load_default=None,
                                validate=[validate.Length(max=100),
                                          validate.Regexp(r'^[A-Za-z0-9\-\.]*$',
                                                          error='Invalid hostname characters')],
                                allow_none=True)

    @validates('ip_address')
    def validate_ip(self, value):
        if value and not _valid_ip(value):
            raise validate.ValidationError('Invalid IP address format')

    @validates('mac_address')
    def validate_mac(self, value):
        if value and not MAC_RE.match(value):
            raise validate.ValidationError('Invalid MAC address format (expected XX:XX:XX:XX:XX:XX)')

    @validates('gateway')
    def validate_gateway(self, value):
        if value and not _valid_ip(value):
            raise validate.ValidationError('Invalid gateway IP format')

    @pre_load
    def strip_strings(self, data, **kwargs):
        return {k: v.strip() if isinstance(v, str) else v for k, v in data.items()}


def _serialize(n: NetworkDetail) -> dict:
    return {
        'asset_id':     n.asset_id,
        'ip_address':   str(n.ip_address)  if n.ip_address  else None,
        'mac_address':  str(n.mac_address) if n.mac_address else None,
        'subnet_mask':  str(n.subnet_mask) if n.subnet_mask else None,
        'gateway':      str(n.gateway)     if n.gateway     else None,
        'dns_primary':  str(n.dns_primary) if n.dns_primary else None,
        'dns_secondary':str(n.dns_secondary) if n.dns_secondary else None,
        'vlan':         n.vlan,
        'hostname':     n.hostname,
        'updated_at':   n.updated_at.isoformat(),
    }


_schema = NetworkSchema()


@api_v1.get('/assets/<int:asset_id>/network')
@require_permission('network:read')
def get_network(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    if not asset.network_detail:
        return jsonify({'data': None}), 200

    return jsonify(_serialize(asset.network_detail)), 200


@api_v1.put('/assets/<int:asset_id>/network')
@require_permission('network:update')
def upsert_network(asset_id: int):
    """Create atau update network detail (upsert)."""
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset:
        return jsonify({'error': 'Asset not found'}), 404

    try:
        data = _schema.load(request.get_json(silent=True) or {})
    except ValidationError as err:
        return jsonify({'errors': err.messages}), 422

    account_id = get_current_account_id()
    old_data   = _serialize(asset.network_detail) if asset.network_detail else None

    if asset.network_detail:
        for key, value in data.items():
            setattr(asset.network_detail, key, value)
        action = 'UPDATE'
    else:
        nd = NetworkDetail(asset_id=asset_id, **data)
        db.session.add(nd)
        action = 'CREATE'

    log_action(account_id, action, 'network', asset_id,
               old_data=old_data, new_data=_serialize(asset.network_detail or nd))
    db.session.commit()

    return jsonify(_serialize(asset.network_detail)), 200


@api_v1.delete('/assets/<int:asset_id>/network')
@require_permission('network:delete')
def delete_network(asset_id: int):
    asset = Asset.query.filter_by(id=asset_id, deleted_at=None).first()
    if not asset or not asset.network_detail:
        return jsonify({'error': 'Network detail not found'}), 404

    account_id = get_current_account_id()
    old_data   = _serialize(asset.network_detail)
    db.session.delete(asset.network_detail)
    log_action(account_id, 'DELETE', 'network', asset_id, old_data=old_data)
    db.session.commit()
    return jsonify({'message': 'Network detail deleted'}), 200
