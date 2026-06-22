"""add list sort indexes

Revision ID: 009_list_sort_indexes
Revises: ef539e472cd2
Create Date: 2026-06-22 00:00:00
"""
from alembic import op


revision = '009_list_sort_indexes'
down_revision = 'ef539e472cd2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_index('ix_assets_model', 'assets', ['model_id'])
    op.create_index('ix_incidents_created', 'incidents', ['created_at'])
    op.create_index('ix_problems_created', 'problems', ['created_at'])
    op.create_index('ix_service_requests_created', 'service_requests', ['created_at'])
    op.create_index('ix_change_requests_created', 'change_requests', ['created_at'])
    op.create_index('ix_checkout_history_asset_created', 'checkout_history', ['asset_id', 'created_at'])
    op.create_index('ix_asset_files_asset_created', 'asset_files', ['asset_id', 'created_at'])


def downgrade():
    op.drop_index('ix_asset_files_asset_created', table_name='asset_files')
    op.drop_index('ix_checkout_history_asset_created', table_name='checkout_history')
    op.drop_index('ix_change_requests_created', table_name='change_requests')
    op.drop_index('ix_service_requests_created', table_name='service_requests')
    op.drop_index('ix_problems_created', table_name='problems')
    op.drop_index('ix_incidents_created', table_name='incidents')
    op.drop_index('ix_assets_model', table_name='assets')
