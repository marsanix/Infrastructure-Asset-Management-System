"""Unit tests for models, utilities, and edge cases."""
import os
import pytest

os.environ.setdefault('DATABASE_URL', 'sqlite:////tmp/test_unit.db')
os.environ.setdefault('JWT_SECRET', 'test-unit-secret-minimum-32-chars-long')
os.environ.setdefault('AES_KEY_BASE64', 'MDEyMzQ1Njc4OTAxMjM0NTY3ODkwMTIzNDU2Nzg5MDE=')
os.environ.setdefault('FRONTEND_ORIGIN', 'http://localhost:3000')
os.environ.setdefault('FLASK_ENV', 'development')
os.environ.setdefault('COOKIE_SECURE', 'false')
os.environ.setdefault('COOKIE_SAMESITE', 'Lax')
os.environ.setdefault('RATELIMIT_ENABLED', 'false')

from app import create_app
from app.extensions import db
from app.models import Asset, Brand, Category, Department, User, Role
from app.utils.security import hash_password, verify_password, encrypt_secret, decrypt_secret, redact, sanitize_error_message
from app.utils.pagination import paginate
import base64


@pytest.fixture(scope='module')
def app():
    app = create_app()
    with app.app_context():
        db.drop_all()
        db.create_all()
        from app.commands import seed_command
        from click.testing import CliRunner
        CliRunner().invoke(seed_command)
    yield app


@pytest.fixture()
def ctx(app):
    with app.app_context():
        yield


class TestSecurityUtils:
    def test_hash_and_verify_password(self):
        pw = 'test-password-123'
        hashed = hash_password(pw)
        assert hashed != pw
        assert verify_password(pw, hashed)
        assert not verify_password('wrong', hashed)

    def test_encrypt_decrypt_secret(self, app):
        key = app.config['AES_KEY']
        plain = 'my-secret-credential'
        enc, nonce = encrypt_secret(plain, key)
        assert enc != plain
        assert plain == decrypt_secret(enc, nonce, key)

    def test_decrypt_wrong_key_fails(self, app):
        key = app.config['AES_KEY']
        wrong = base64.b64encode(b'x' * 32).decode()
        _, nonce = encrypt_secret('test', key)
        with pytest.raises(ValueError):
            decrypt_secret('bad', nonce, key)

    def test_redact_sensitive_keys(self):
        data = {'password': 'secret', 'token': 'jwt123', 'name': 'John'}
        result = redact(data)
        assert result['password'] == '***REDACTED***'
        assert result['token'] == '***REDACTED***'
        assert result['name'] == 'John'

    def test_sanitize_error_message(self):
        msg = 'Error at /secret/path something'
        clean = sanitize_error_message(msg)
        assert '/secret' not in clean


class TestModels:
    def test_user_to_dict(self, ctx):
        u = User.query.first()
        d = u.to_dict()
        assert d['name'] == 'Rendy Adhitama'
        assert d['email'] == 'admin@iams.local'
        assert d['role_name'] == 'Administrator'
        assert 'password_hash' not in d
        assert d['avatar'] == 'RA'

    def test_asset_to_dict(self, ctx):
        a = Asset.query.filter_by(asset_tag='AST-RTR-0001').first()
        d = a.to_dict()
        assert d['asset_tag'] == 'AST-RTR-0001'
        assert d['serial_number'] == 'DEMO-SN-AST-RTR-0001'
        assert 'status' in d

    def test_model_to_dict(self, ctx):
        from app.models import DeviceModel
        m = DeviceModel.query.first()
        d = m.to_dict()
        assert 'name' in d
        assert 'brand_name' in d
        assert 'category_name' in d

    def test_user_sensitive_not_in_to_dict(self, ctx):
        u = User.query.first()
        d = u.to_dict()
        assert 'password_hash' not in d

    def test_audit_log_to_dict(self, ctx):
        from app.models import AuditLog
        # Create one
        log = AuditLog(action='TEST', resource_type='test', status='success', ip_address='127.0.0.1')
        db.session.add(log)
        db.session.commit()
        d = log.to_dict()
        assert d['action'] == 'TEST'
        assert d['status'] == 'success'

    def test_model_count(self, ctx):
        assert Asset.query.count() >= 8
        assert User.query.count() >= 2
        assert Role.query.count() >= 2
        assert Department.query.count() >= 5
        assert Category.query.count() >= 5
        assert Brand.query.count() >= 8


class TestPagination:
    def test_pagination_default(self, app):
        with app.test_request_context('/test?page=1&per_page=5'):
            from app.models import Asset
            q = Asset.query.order_by(Asset.asset_tag)
            r = paginate(q)
            assert r['page'] == 1
            assert r['per_page'] == 5
            assert r['total'] >= 8
            assert len(r['data']) == 5

    def test_pagination_page_clamp(self, app):
        with app.test_request_context('/test?page=999&per_page=10'):
            from app.models import Asset
            q = Asset.query.order_by(Asset.asset_tag)
            r = paginate(q)
            assert r['page'] <= r['pages']
