"""Reports blueprint (Administrator only)."""
from datetime import datetime, timedelta, timezone

from flask import Blueprint, jsonify, request
from sqlalchemy import func
from sqlalchemy.orm import selectinload

from app.models import Asset, DeviceModel, User
from app.utils.decorators import admin_only
from app.utils.pagination import paginate

bp = Blueprint('reports', __name__, url_prefix='/api/reports')


@bp.route('/assets/full', methods=['GET'])
@admin_only
def full_asset_report():
    rows = Asset.query.options(
        selectinload(Asset.model).selectinload(DeviceModel.brand),
        selectinload(Asset.model).selectinload(DeviceModel.category),
        selectinload(Asset.location),
        selectinload(Asset.user).selectinload(User.department),
        selectinload(Asset.network_detail),
    ).order_by(Asset.asset_tag)
    return jsonify(paginate(rows, max_per_page=500))


@bp.route('/assets/status-summary', methods=['GET'])
@admin_only
def status_summary():
    summary = dict(db_row for db_row in Asset.query.with_entities(Asset.status, func.count(Asset.id)).group_by(Asset.status))
    summary['total'] = sum(summary.values())
    return {'data': summary}


@bp.route('/assets/by-po', methods=['GET'])
@admin_only
def by_po():
    po = (request.args.get('po_number') or '').strip()
    if not po:
        return {'error': 'po_number is required'}, 400
    assets = Asset.query.filter(Asset.po_number.like(f'{po}%')).order_by(Asset.asset_tag)
    return jsonify(paginate(assets))


@bp.route('/assets/warranty-expiring', methods=['GET'])
@admin_only
def warranty_expiring():
    try:
        months = int(request.args.get('months', 3))
    except ValueError:
        return {'error': 'months must be an integer'}, 400

    today = datetime.now(timezone.utc).date()
    threshold = today + timedelta(days=months * 30)
    assets = Asset.query.options(
        selectinload(Asset.model),
        selectinload(Asset.location),
        selectinload(Asset.user),
    ).filter(
        Asset.purchase_date.isnot(None),
        Asset.warranty_months.isnot(None),
    ).order_by(Asset.purchase_date).limit(500).all()
    result = []
    for a in assets:
        if not a.purchase_date or not a.warranty_months:
            continue
        expiry = a.purchase_date + timedelta(days=a.warranty_months * 30)
        remaining = (expiry - today).days
        if expiry <= threshold:
            data = a.to_dict()
            data['warranty_expiry'] = expiry.isoformat()
            data['warranty_remaining_days'] = max(0, remaining)
            data['warranty_status'] = 'expired' if remaining < 0 else 'expiring'
            result.append(data)
    return {'data': result}
