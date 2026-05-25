"""
Database seeder — IAMS initial data.

Security:
- Password admin diambil dari environment variable, TIDAK hardcode
- Seed bersifat idempotent — aman dijalankan berulang kali
- Tidak ada plaintext password di file ini
- Roles dan permissions di-seed sesuai database.sql

Cara pakai:
    python seed.py
"""
import os
import sys

# Pastikan .env ter-load sebelum import app
from dotenv import load_dotenv
load_dotenv()

from run import app
from app.extensions import db
from app.models.role import Role, Permission, RolePermission
from app.models.account import Account
from app.models.department import Department
from app.models.location import Location
from app.models.category import Category
from app.models.brand import Brand
from app.models.model_device import DeviceModel


def seed_roles_and_permissions():
    """Seed roles dan permissions — idempotent."""
    print('Seeding roles and permissions...')

    # Roles
    roles_data = [
        {'name': 'Administrator', 'description': 'Full access to all modules'},
        {'name': 'User',          'description': 'Limited access, read-only on most modules'},
    ]
    for r in roles_data:
        if not Role.query.filter_by(name=r['name']).first():
            db.session.add(Role(**r))
    db.session.flush()

    # Permissions
    perms_data = [
        # Asset
        ('asset:create',      'asset',      'create'),
        ('asset:read',        'asset',      'read'),
        ('asset:update',      'asset',      'update'),
        ('asset:delete',      'asset',      'delete'),
        # Account
        ('account:create',    'account',    'create'),
        ('account:read',      'account',    'read'),
        ('account:update',    'account',    'update'),
        ('account:delete',    'account',    'delete'),
        # Department
        ('department:create', 'department', 'create'),
        ('department:read',   'department', 'read'),
        ('department:update', 'department', 'update'),
        ('department:delete', 'department', 'delete'),
        # Location
        ('location:create',   'location',   'create'),
        ('location:read',     'location',   'read'),
        ('location:update',   'location',   'update'),
        ('location:delete',   'location',   'delete'),
        # Category
        ('category:create',   'category',   'create'),
        ('category:read',     'category',   'read'),
        ('category:update',   'category',   'update'),
        ('category:delete',   'category',   'delete'),
        # Brand
        ('brand:create',      'brand',      'create'),
        ('brand:read',        'brand',      'read'),
        ('brand:update',      'brand',      'update'),
        ('brand:delete',      'brand',      'delete'),
        # Model
        ('model:create',      'model',      'create'),
        ('model:read',        'model',      'read'),
        ('model:update',      'model',      'update'),
        ('model:delete',      'model',      'delete'),
        # Network
        ('network:create',    'network',    'create'),
        ('network:read',      'network',    'read'),
        ('network:update',    'network',    'update'),
        ('network:delete',    'network',    'delete'),
        # Credential
        ('credential:create', 'credential', 'create'),
        ('credential:read',   'credential', 'read'),
        ('credential:update', 'credential', 'update'),
        ('credential:delete', 'credential', 'delete'),
        # ITSM
        ('incident:create',   'incident',   'create'),
        ('incident:read',     'incident',   'read'),
        ('incident:update',   'incident',   'update'),
        ('incident:delete',   'incident',   'delete'),
        ('change:create',     'change',     'create'),
        ('change:read',       'change',     'read'),
        ('change:update',     'change',     'update'),
        ('change:delete',     'change',     'delete'),
        ('problem:create',    'problem',    'create'),
        ('problem:read',      'problem',    'read'),
        ('problem:update',    'problem',    'update'),
        ('problem:delete',    'problem',    'delete'),
        ('request:create',    'request',    'create'),
        ('request:read',      'request',    'read'),
        ('request:update',    'request',    'update'),
        ('request:delete',    'request',    'delete'),
        # Report & Audit
        ('report:read',       'report',     'read'),
        ('audit:read',        'audit',      'read'),
    ]

    for name, module, action in perms_data:
        if not Permission.query.filter_by(name=name).first():
            db.session.add(Permission(name=name, module=module, action=action))
    db.session.flush()

    # Administrator mendapat semua permission
    admin_role = Role.query.filter_by(name='Administrator').first()
    all_perms  = Permission.query.all()
    for perm in all_perms:
        if not RolePermission.query.filter_by(
            role_id=admin_role.id, permission_id=perm.id
        ).first():
            db.session.add(RolePermission(role_id=admin_role.id, permission_id=perm.id))

    # User mendapat permission terbatas
    user_role = Role.query.filter_by(name='User').first()
    user_perms = [
        'asset:read', 'department:read', 'location:read', 'category:read',
        'brand:read', 'model:read', 'network:read',
        'incident:create', 'incident:read',
        'change:read', 'problem:read',
        'request:create', 'request:read',
        'report:read',
    ]
    for perm_name in user_perms:
        perm = Permission.query.filter_by(name=perm_name).first()
        if perm and not RolePermission.query.filter_by(
            role_id=user_role.id, permission_id=perm.id
        ).first():
            db.session.add(RolePermission(role_id=user_role.id, permission_id=perm.id))

    db.session.commit()
    print('  ✓ Roles and permissions seeded')


def seed_admin_account():
    """
    Seed akun admin dari environment variables.
    Password TIDAK hardcode — wajib set di .env.
    """
    print('Seeding admin account...')

    username = os.environ.get('ADMIN_USERNAME', 'admin')
    email    = os.environ.get('ADMIN_EMAIL',    'admin@example.com')
    password = os.environ.get('ADMIN_PASSWORD', '')
    fullname = os.environ.get('ADMIN_FULLNAME', 'System Administrator')

    if not password:
        print('  ✗ ADMIN_PASSWORD not set in .env — skipping admin seed')
        print('    Set ADMIN_PASSWORD in .env and re-run seed.py')
        return

    if len(password) < 8:
        print('  ✗ ADMIN_PASSWORD too short (min 8 chars) — skipping')
        return

    if Account.query.filter_by(username=username, deleted_at=None).first():
        print(f'  ℹ Admin account "{username}" already exists — skipping')
        return

    admin_role = Role.query.filter_by(name='Administrator').first()
    if not admin_role:
        print('  ✗ Administrator role not found — run seed_roles first')
        return

    acc = Account(
        username  = username,
        email     = email,
        full_name = fullname,
        role_id   = admin_role.id,
        is_active = True,
    )
    acc.set_password(password)
    db.session.add(acc)
    db.session.commit()
    print(f'  ✓ Admin account "{username}" created')


def seed_master_data():
    """Seed data master awal — idempotent."""
    print('Seeding master data...')

    # Departments
    depts = ['IT Infrastructure', 'Finance', 'HR', 'Operations', 'Marketing', 'Management']
    for name in depts:
        if not Department.query.filter_by(name=name).first():
            db.session.add(Department(name=name))

    # Locations
    locs = [
        ('Server Room',    'Main server room'),
        ('Office Floor 1', 'First floor office area'),
        ('Office Floor 2', 'Second floor office area'),
        ('Warehouse',      'IT equipment storage'),
        ('Remote',         'Remote/WFH location'),
    ]
    for name, desc in locs:
        if not Location.query.filter_by(name=name).first():
            db.session.add(Location(name=name, description=desc))

    # Categories
    cats = ['Laptop', 'Desktop', 'Server', 'Network Switch', 'Router', 'Firewall',
            'Access Point', 'Printer', 'UPS', 'Monitor', 'Storage', 'Other']
    for name in cats:
        if not Category.query.filter_by(name=name).first():
            db.session.add(Category(name=name))

    # Brands
    brands = ['Dell', 'HP', 'Lenovo', 'Apple', 'Cisco', 'Mikrotik', 'Fortinet',
              'Ubiquiti', 'TP-Link', 'Samsung', 'Epson', 'Canon', 'APC', 'Synology']
    for name in brands:
        if not Brand.query.filter_by(name=name).first():
            db.session.add(Brand(name=name))

    db.session.commit()
    print('  ✓ Master data seeded')


def main():
    with app.app_context():
        print('=== IAMS Database Seeder ===')
        print(f'Environment: {os.environ.get("FLASK_ENV", "production")}')
        print()

        try:
            seed_roles_and_permissions()
            seed_admin_account()
            seed_master_data()
            print()
            print('=== Seeding completed successfully ===')
        except Exception as e:
            db.session.rollback()
            print(f'\n✗ Seeding failed: {e}')
            sys.exit(1)


if __name__ == '__main__':
    main()
