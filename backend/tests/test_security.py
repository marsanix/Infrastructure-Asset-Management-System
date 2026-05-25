"""
Security tests — memverifikasi header keamanan, CORS, dan API protection.
Sesuai OWASP Top 10:2025.
"""
import json
import pytest


def post_json(client, url, data, headers=None):
    return client.post(url, data=json.dumps(data),
                       content_type="application/json", headers=headers or {})


class TestSecurityHeaders:
    """OWASP A05 — Security Misconfiguration."""

    def test_x_content_type_options_header(self, client):
        rv = client.get("/api/health")
        assert rv.headers.get("X-Content-Type-Options") == "nosniff"

    def test_x_frame_options_header(self, client):
        rv = client.get("/api/health")
        # Flask-Talisman sets this
        xfo = rv.headers.get("X-Frame-Options", "")
        csp = rv.headers.get("Content-Security-Policy", "")
        # Salah satu harus ada
        assert "SAMEORIGIN" in xfo or "DENY" in xfo or "frame-ancestors" in csp

    def test_content_security_policy_present(self, client):
        rv = client.get("/api/health")
        assert "Content-Security-Policy" in rv.headers
        csp = rv.headers["Content-Security-Policy"]
        assert "default-src" in csp

    def test_csp_no_unsafe_eval(self, client):
        rv = client.get("/api/health")
        csp = rv.headers.get("Content-Security-Policy", "")
        assert "unsafe-eval" not in csp

    def test_referrer_policy_present(self, client):
        rv = client.get("/api/health")
        assert "Referrer-Policy" in rv.headers


class TestUnauthorizedAccess:
    """OWASP A01 / API1 — Broken Access Control."""

    def test_assets_without_token_returns_401(self, client):
        rv = client.get("/api/v1/assets")
        assert rv.status_code == 401

    def test_accounts_without_token_returns_401(self, client):
        rv = client.get("/api/v1/accounts")
        assert rv.status_code == 401

    def test_audit_logs_without_token_returns_401(self, client):
        rv = client.get("/api/v1/audit-logs")
        assert rv.status_code == 401

    def test_invalid_token_returns_401(self, client):
        headers = {"Authorization": "Bearer totally_invalid_token"}
        rv = client.get("/api/v1/assets", headers=headers)
        assert rv.status_code == 422  # JWT Extended: invalid token format

    def test_malformed_authorization_header(self, client):
        headers = {"Authorization": "NotBearer something"}
        rv = client.get("/api/v1/assets", headers=headers)
        assert rv.status_code in (401, 422)


class TestInsufficientPermissions:
    """RBAC — pengguna dengan permission terbatas tidak bisa akses endpoint lain."""

    def test_read_only_user_cannot_create_asset(self, client, make_account, app, make_model, make_location):
        account = make_account(
            username="readonly",
            password="Read@Only1!",
            permissions=["asset:read"],
        )
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(account.id))
        headers = {"Authorization": f"Bearer {token}"}

        model = make_model(name="ReadOnlyModel")
        location = make_location(name="ReadOnlyLoc", code="ROL")

        rv = post_json(client, "/api/v1/assets", {
            "asset_tag": "NO-PERM-001",
            "serial_number": "NP-SN-001",
            "model_id": model.id,
            "location_id": location.id,
        }, headers)
        assert rv.status_code == 403

    def test_read_only_user_cannot_delete_asset(self, client, make_account, make_asset, app):
        asset = make_asset(asset_tag="PERM-DEL-01", serial_number="PD001")
        account = make_account(
            username="nodeletion",
            password="NoDel@1!",
            permissions=["asset:read"],
        )
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(account.id))
        headers = {"Authorization": f"Bearer {token}"}

        rv = client.delete(f"/api/v1/assets/{asset.id}", headers=headers)
        assert rv.status_code == 403


class TestInputValidationSecurity:
    """OWASP A03 — Injection prevention."""

    def test_sql_injection_in_search_param(self, client, auth_headers):
        """SQL injection string via search param — harus aman (ORM)."""
        _, headers = auth_headers
        malicious = "'; DROP TABLE assets; --"
        rv = client.get(f"/api/v1/assets?search={malicious}", headers=headers)
        # Harus return 200 dengan empty result — bukan error 500
        assert rv.status_code == 200

    def test_xss_in_asset_tag_rejected(self, client, auth_headers, make_model, make_location):
        """Script injection dalam asset_tag — harus ditolak oleh validasi."""
        model = make_model(name="XSSModel")
        location = make_location(name="XSSLoc", code="XSS")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "<script>alert('xss')</script>",
            "serial_number": "XSS-SN-001",
            "model_id":      model.id,
            "location_id":   location.id,
        }, headers)
        assert rv.status_code == 422  # Ditolak validasi regex

    def test_oversized_per_page_capped(self, client, auth_headers):
        """Tidak boleh request terlalu banyak data sekaligus (API4)."""
        _, headers = auth_headers
        rv = client.get("/api/v1/assets?per_page=10000", headers=headers)
        assert rv.status_code == 200
        assert rv.get_json()["per_page"] <= 100

    def test_empty_json_body_handled_gracefully(self, client, auth_headers):
        """Empty body saat POST — tidak boleh crash."""
        _, headers = auth_headers
        rv = client.post("/api/v1/assets",
                         data="", content_type="application/json",
                         headers=headers)
        assert rv.status_code == 422  # validation error, bukan 500

    def test_login_error_does_not_reveal_which_field_wrong(self, client, make_account):
        """Generic error — tidak reveal username vs password yang salah."""
        make_account(username="generic_err", password="Real@Pass1!")

        # Username benar, password salah
        rv1 = post_json(client, "/api/v1/auth/login", {
            "username": "generic_err", "password": "WrongPass@1!"
        })
        # Username salah
        rv2 = post_json(client, "/api/v1/auth/login", {
            "username": "non_existent_user_xyz", "password": "AnyPass@1!"
        })

        assert rv1.status_code == rv2.status_code == 401
        assert rv1.get_json()["error"] == rv2.get_json()["error"]  # pesan sama
