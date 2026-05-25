"""
Shared pytest fixtures untuk IAMS backend tests.

Strategi:
- SQLite in-memory untuk isolasi total (tidak perlu PostgreSQL nyata)
- Redis di-mock agar tidak butuh koneksi real
- Fixtures scope 'session' untuk app + db schema (dibuat sekali)
- Fixtures scope 'function' untuk data (di-rollback setiap test)
"""
import os
import pytest
from unittest.mock import MagicMock, patch

# Set env vars SEBELUM import app — config.py membaca env saat module load
os.environ.setdefault("SECRET_KEY",           "test-secret-key-32-chars-minimum!!")
os.environ.setdefault("JWT_SECRET_KEY",       "test-jwt-secret-key-32-chars-ok!!")
os.environ.setdefault("POSTGRES_USER",        "test")
os.environ.setdefault("POSTGRES_PASSWORD",    "test")
os.environ.setdefault("POSTGRES_HOST",        "localhost")
os.environ.setdefault("POSTGRES_DB",          "test")
os.environ.setdefault("REDIS_PASSWORD",       "test")
os.environ.setdefault("REDIS_HOST",           "localhost")
os.environ.setdefault("AES_ENCRYPTION_KEY",   "Hn0_lqStjI2pQj7djCZi-6hA3F4v8W_g2DEMp6uN0bI=")
os.environ.setdefault("CORS_ORIGINS",         "http://localhost:5173")


@pytest.fixture(scope="session")
def app():
    """App factory dengan testing config, Redis di-mock."""
    # Mock Redis sebelum app dibuat
    with patch("redis.from_url") as mock_redis_factory:
        mock_redis_inst = MagicMock()
        mock_redis_inst.exists.return_value = 0
        mock_redis_inst.setex.return_value  = True
        mock_redis_factory.return_value     = mock_redis_inst

        from app import create_app
        application = create_app("testing")
        application.config["REDIS_MOCK"] = mock_redis_inst
        yield application


@pytest.fixture(scope="session")
def db_instance(app):
    """Buat semua tabel sekali per sesi test."""
    from app.extensions import db as _db
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture(autouse=True)
def db_session(db_instance, app):
    """
    Setiap test berjalan dalam app context, lalu hapus semua data setelahnya.
    Menjamin isolasi antar test tanpa perlu nested transaction (SQLAlchemy 2.0 compat).
    """
    with app.app_context():
        yield db_instance.session
        db_instance.session.rollback()
        # Bersihkan semua tabel setelah setiap test
        for table in reversed(db_instance.metadata.sorted_tables):
            db_instance.session.execute(table.delete())
        db_instance.session.commit()


@pytest.fixture
def client(app):
    """Test client Flask."""
    return app.test_client()


# ── Data factories ────────────────────────────────────────────

@pytest.fixture
def make_role(db_session):
    """Factory untuk membuat Role + Permission."""
    from app.models.role import Role, Permission

    def _make(name="Admin", permissions=None):
        # Gunakan is None check, bukan `or` — [] adalah valid (empty permissions)
        if permissions is None:
            permissions = ["asset:read", "asset:create", "asset:update", "asset:delete"]
        role = Role(name=name, description=f"Role {name}")
        db_session.add(role)
        db_session.flush()

        for perm_name in permissions:
            module, action = perm_name.split(":")
            perm = Permission.query.filter_by(name=perm_name).first()
            if not perm:
                perm = Permission(name=perm_name, module=module, action=action)
                db_session.add(perm)
                db_session.flush()
            role.permissions.append(perm)

        db_session.flush()
        return role

    return _make


@pytest.fixture
def make_account(db_session, make_role):
    """Factory untuk membuat Account dengan role + password."""
    from app.models.account import Account

    def _make(username="testuser", password="Test@1234!", role=None, is_active=True, permissions=None):
        if role is None:
            role = make_role(name=f"Role_{username}", permissions=permissions or [
                "asset:read", "asset:create", "asset:update", "asset:delete",
                "account:read", "account:create", "account:update",
                "audit:read",
            ])
        account = Account(
            username=username,
            email=f"{username}@test.com",
            full_name=f"Test {username}",
            role_id=role.id,
            is_active=is_active,
        )
        account.set_password(password)
        db_session.add(account)
        db_session.flush()
        return account

    return _make


@pytest.fixture
def auth_headers(client, make_account, app):
    """Fixture yang return (account, headers) — headers sudah punya Bearer token."""
    account = make_account(username="admin_user", password="Admin@5678!")

    with app.app_context():
        from flask_jwt_extended import create_access_token
        token = create_access_token(identity=str(account.id))

    return account, {"Authorization": f"Bearer {token}"}


@pytest.fixture
def make_department(db_session):
    from app.models.department import Department

    def _make(name="IT", description="IT Dept"):
        dept = Department(name=name, description=description)
        db_session.add(dept)
        db_session.flush()
        return dept

    return _make


@pytest.fixture
def make_location(db_session):
    from app.models.location import Location

    def _make(name="Server Room", **kwargs):
        loc = Location(name=name)
        db_session.add(loc)
        db_session.flush()
        return loc

    return _make


@pytest.fixture
def make_brand(db_session):
    from app.models.brand import Brand

    def _make(name="Dell"):
        brand = Brand(name=name)
        db_session.add(brand)
        db_session.flush()
        return brand

    return _make


@pytest.fixture
def make_category(db_session):
    from app.models.category import Category

    def _make(name="Server"):
        cat = Category(name=name)
        db_session.add(cat)
        db_session.flush()
        return cat

    return _make


@pytest.fixture
def make_model(db_session, make_brand, make_category):
    from app.models.model_device import DeviceModel

    def _make(name="PowerEdge R750", brand=None, category=None):
        if brand is None:
            brand = make_brand()
        if category is None:
            category = make_category()
        model = DeviceModel(name=name, brand_id=brand.id, category_id=category.id)
        db_session.add(model)
        db_session.flush()
        return model

    return _make


@pytest.fixture
def make_asset(db_session, make_model, make_location):
    from app.models.asset import Asset

    def _make(asset_tag="SRV-0001", serial_number="SN001", model=None, location=None, status="Available"):
        if model is None:
            model = make_model()
        if location is None:
            location = make_location()
        asset = Asset(
            asset_tag=asset_tag,
            serial_number=serial_number,
            model_id=model.id,
            location_id=location.id,
            status=status,
        )
        db_session.add(asset)
        db_session.flush()
        return asset

    return _make
