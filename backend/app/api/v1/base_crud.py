"""
Generic CRUD factory untuk master data modules.

Security per endpoint:
- RBAC via require_permission (OWASP A01)
- Input validation via Marshmallow EXCLUDE (API3 Mass Assignment)
- Explicit serializer — tidak pernah expose semua kolom model (API3 Excessive Data Exposure)
- Pagination max 200 untuk master data (API4 Resource Consumption)
- Search via ORM ilike — tidak ada raw SQL (OWASP A03)
- Soft delete — data tidak hilang permanen
- Audit log setiap mutasi
- 404 response tidak membedakan "not found" vs "no permission" (BOLA prevention)
"""
from datetime import datetime, timezone
from typing import Any, Callable

from flask import request, jsonify, Blueprint
from ...utils.rbac import get_current_account_id
from marshmallow import Schema, ValidationError

from ...extensions import db
from ...utils.rbac import require_permission
from ...utils.audit import log_action


def register_crud(
    blueprint:         Blueprint,
    url_prefix:        str,
    model_class:       Any,
    create_schema:     Schema,
    update_schema:     Schema,
    serializer:        Callable[[Any], dict],
    permission_module: str,
    searchable_fields: list[Any] | None = None,
    max_per_page:      int = 200,
    soft_delete:       bool = True,
) -> None:
    """
    Daftarkan 5 endpoint CRUD ke blueprint dengan nama endpoint unik
    berdasarkan permission_module — mencegah Flask endpoint name conflict.
    """
    # Nama unik per modul — kunci fix untuk AssertionError endpoint conflict
    ep = permission_module  # e.g. 'department', 'location', 'brand'

    # ── LIST ──────────────────────────────────────────────────
    @blueprint.get(url_prefix, endpoint=f'{ep}_list')
    @require_permission(f'{permission_module}:read')
    def _list():
        try:
            page     = max(1, int(request.args.get('page', 1)))
            per_page = min(max(1, int(request.args.get('per_page', 50))), max_per_page)
        except (ValueError, TypeError):
            return jsonify({'error': 'Invalid pagination parameters'}), 400

        search = request.args.get('search', '').strip()[:100]

        query = model_class.query
        if soft_delete and hasattr(model_class, 'deleted_at'):
            query = query.filter(model_class.deleted_at.is_(None))

        active_only = request.args.get('active_only', 'true').lower() == 'true'
        if active_only and hasattr(model_class, 'is_active'):
            query = query.filter(model_class.is_active.is_(True))

        if search and searchable_fields:
            like = f'%{search}%'
            conditions = [col.ilike(like) for col in searchable_fields]
            query = query.filter(db.or_(*conditions))

        if hasattr(model_class, 'name'):
            query = query.order_by(model_class.name)
        else:
            query = query.order_by(model_class.id)

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return jsonify({
            'data':     [serializer(item) for item in pagination.items],
            'total':    pagination.total,
            'page':     pagination.page,
            'per_page': pagination.per_page,
            'pages':    pagination.pages,
        }), 200

    # ── GET ONE ───────────────────────────────────────────────
    @blueprint.get(f'{url_prefix}/<int:item_id>', endpoint=f'{ep}_get')
    @require_permission(f'{permission_module}:read')
    def _get(item_id: int):
        item = _get_active(model_class, item_id, soft_delete)
        if not item:
            return jsonify({'error': f'{permission_module.capitalize()} not found'}), 404
        return jsonify(serializer(item)), 200

    # ── CREATE ────────────────────────────────────────────────
    @blueprint.post(url_prefix, endpoint=f'{ep}_create')
    @require_permission(f'{permission_module}:create')
    def _create():
        try:
            data = create_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 422

        account_id = get_current_account_id()
        item = model_class(**data)
        db.session.add(item)
        db.session.flush()

        log_action(account_id, 'CREATE', permission_module, item.id,
                   new_data=serializer(item))
        db.session.commit()

        return jsonify(serializer(item)), 201

    # ── UPDATE ────────────────────────────────────────────────
    @blueprint.put(f'{url_prefix}/<int:item_id>', endpoint=f'{ep}_update')
    @require_permission(f'{permission_module}:update')
    def _update(item_id: int):
        item = _get_active(model_class, item_id, soft_delete)
        if not item:
            return jsonify({'error': f'{permission_module.capitalize()} not found'}), 404

        try:
            data = update_schema.load(
                request.get_json(silent=True) or {}, partial=True
            )
        except ValidationError as err:
            return jsonify({'errors': err.messages}), 422

        if not data:
            return jsonify({'error': 'No valid fields to update'}), 400

        old_data   = serializer(item)
        account_id = get_current_account_id()

        for key, value in data.items():
            setattr(item, key, value)

        log_action(account_id, 'UPDATE', permission_module, item.id,
                   old_data=old_data, new_data=serializer(item))
        db.session.commit()

        return jsonify(serializer(item)), 200

    # ── DELETE ────────────────────────────────────────────────
    @blueprint.delete(f'{url_prefix}/<int:item_id>', endpoint=f'{ep}_delete')
    @require_permission(f'{permission_module}:delete')
    def _delete(item_id: int):
        item = _get_active(model_class, item_id, soft_delete)
        if not item:
            return jsonify({'error': f'{permission_module.capitalize()} not found'}), 404

        old_data   = serializer(item)
        account_id = get_current_account_id()

        if soft_delete and hasattr(item, 'deleted_at'):
            item.deleted_at = datetime.now(timezone.utc)
        else:
            db.session.delete(item)

        log_action(account_id, 'DELETE', permission_module, item.id, old_data=old_data)
        db.session.commit()

        return jsonify({'message': f'{permission_module.capitalize()} deleted successfully'}), 200


def _get_active(model_class: Any, item_id: int, soft_delete: bool) -> Any | None:
    """Helper: ambil record aktif, return None jika tidak ada."""
    query = model_class.query.filter_by(id=item_id)
    if soft_delete and hasattr(model_class, 'deleted_at'):
        query = query.filter(model_class.deleted_at.is_(None))
    return query.first()
