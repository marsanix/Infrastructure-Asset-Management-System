"""Dashboard summary endpoints."""
from flask import Blueprint, jsonify
from sqlalchemy import func

from app.extensions import db
from app.models import Asset, Category, DeviceModel, Incident, Problem
from app.utils.decorators import admin_or_operator

bp = Blueprint('dashboard', __name__, url_prefix='/api/dashboard')


def _counts(model, column):
    return dict(db.session.query(column, func.count(model.id)).group_by(column).all())


@bp.route('/summary', methods=['GET'])
@admin_or_operator
def summary():
    asset_status = _counts(Asset, Asset.status)
    incident_status = _counts(Incident, Incident.status)
    incident_severity = _counts(Incident, Incident.severity)
    problem_status = _counts(Problem, Problem.status)
    assets_by_category = dict(
        db.session.query(Category.name, func.count(Asset.id))
        .join(DeviceModel, Asset.model_id == DeviceModel.id)
        .join(Category, DeviceModel.category_id == Category.id)
        .group_by(Category.name)
        .all()
    )
    return jsonify({'data': {
        'total_assets': sum(asset_status.values()),
        'asset_status': asset_status,
        'open_incidents': sum(incident_status.get(s, 0) for s in ('Open', 'In Progress')),
        'critical_incidents': incident_severity.get('Critical', 0),
        'active_problems': sum(c for s, c in problem_status.items() if s != 'Closed'),
        'assets_by_category': assets_by_category,
    }})
