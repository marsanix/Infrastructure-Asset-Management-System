"""upgrade asset_credentials: 1:1 → 1:N, add credential_type/username/notes

Revision ID: 006_multi_credentials
Revises: 005_perf_indexes
Create Date: 2026-06-19 00:30:00
"""
from alembic import op
import sqlalchemy as sa


revision = '006_multi_credentials'
down_revision = '005_perf_indexes'
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c['name'] for c in inspector.get_columns('asset_credentials')]

    if 'credential_type' not in columns:
        op.add_column('asset_credentials', sa.Column('credential_type', sa.String(length=50), nullable=False, server_default='SSH'))
    if 'username' not in columns:
        op.add_column('asset_credentials', sa.Column('username', sa.String(length=255), nullable=True))
    if 'notes' not in columns:
        op.add_column('asset_credentials', sa.Column('notes', sa.Text(), nullable=True))

    # Drop unique constraint on asset_id (auto-named by MariaDB)
    indexes = [i['name'] for i in inspector.get_indexes('asset_credentials')]
    with op.batch_alter_table('asset_credentials') as batch_op:
        # Create the non-unique index first so the foreign key constraint has a backing index
        if 'ix_asset_credentials_asset' not in indexes:
            batch_op.create_index('ix_asset_credentials_asset', ['asset_id'])
        # Now drop the unique index
        if 'asset_id' in indexes:
            batch_op.drop_index('asset_id')


def downgrade():
    with op.batch_alter_table('asset_credentials') as batch_op:
        batch_op.drop_index('ix_asset_credentials_asset')
        batch_op.create_unique_constraint('uq_asset_credentials_asset', ['asset_id'])
    op.drop_column('asset_credentials', 'notes')
    op.drop_column('asset_credentials', 'username')
    op.drop_column('asset_credentials', 'credential_type')
