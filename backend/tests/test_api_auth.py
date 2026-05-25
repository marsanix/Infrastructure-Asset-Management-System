"""
Integration tests: /api/v1/auth/*
Covers: login, logout, refresh, /me
"""
import json
import pytest


def post_json(client, url, data):
    return client.post(url, data=json.dumps(data), content_type="application/json")


class TestLogin:
    def test_login_success(self, client, make_account):
        make_account(username="login_ok", password="Login@Pass1!")
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "login_ok",
            "password": "Login@Pass1!",
        })
        assert rv.status_code == 200
        body = rv.get_json()
        assert "access_token"  in body
        assert "refresh_token" in body
        assert body["user"]["username"] == "login_ok"
        assert "permissions" in body["user"]

    def test_login_wrong_password(self, client, make_account):
        make_account(username="login_bad", password="Correct@Pass1!")
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "login_bad",
            "password": "Wrong@Pass1!",
        })
        assert rv.status_code == 401
        body = rv.get_json()
        assert body["error"] == "Invalid credentials"

    def test_login_nonexistent_user(self, client):
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "ghost_user",
            "password": "AnyPass@123!",
        })
        assert rv.status_code == 401
        # Generic error — tidak boleh reveal mana yang salah
        assert rv.get_json()["error"] == "Invalid credentials"

    def test_login_empty_payload(self, client):
        rv = post_json(client, "/api/v1/auth/login", {})
        assert rv.status_code == 400

    def test_login_missing_password(self, client):
        rv = post_json(client, "/api/v1/auth/login", {"username": "someone"})
        assert rv.status_code == 400

    def test_login_inactive_account(self, client, make_account):
        make_account(username="inactive_user", password="Pass@123!", is_active=False)
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "inactive_user",
            "password": "Pass@123!",
        })
        assert rv.status_code == 401

    def test_login_locked_account(self, client, make_account, db_session):
        account = make_account(username="locked_user", password="Lock@Pass1!")
        for _ in range(5):
            account.increment_failed_login()
        db_session.flush()

        rv = post_json(client, "/api/v1/auth/login", {
            "username": "locked_user",
            "password": "Lock@Pass1!",
        })
        assert rv.status_code == 403
        assert "locked" in rv.get_json()["error"].lower()

    def test_login_brute_force_locks_after_5_attempts(self, client, make_account, db_session):
        account = make_account(username="brute_test", password="Real@Pass1!")
        db_session.flush()

        for _ in range(5):
            rv = post_json(client, "/api/v1/auth/login", {
                "username": "brute_test",
                "password": "Wrong@Pass!",
            })
            assert rv.status_code == 401

        # Setelah 5 kali — akun harus terkunci
        db_session.refresh(account)
        assert account.is_locked is True

    def test_login_response_never_exposes_password_hash(self, client, make_account):
        make_account(username="hash_expose", password="Hash@Expose1!")
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "hash_expose",
            "password": "Hash@Expose1!",
        })
        response_text = rv.get_data(as_text=True)
        assert "password_hash" not in response_text
        assert "$2b$" not in response_text


class TestAuthMe:
    def test_me_requires_token(self, client):
        rv = client.get("/api/v1/auth/me")
        assert rv.status_code == 401

    def test_me_returns_user_data(self, client, auth_headers, app):
        _, headers = auth_headers
        rv = client.get("/api/v1/auth/me", headers=headers)
        assert rv.status_code == 200
        body = rv.get_json()
        assert "id" in body
        assert "username" in body
        assert "password_hash" not in body  # tidak boleh expose hash


class TestAuthRefresh:
    def test_refresh_with_valid_refresh_token(self, client, make_account, app):
        make_account(username="refresh_test", password="Refresh@Pass1!")
        # Login dulu
        rv = post_json(client, "/api/v1/auth/login", {
            "username": "refresh_test",
            "password": "Refresh@Pass1!",
        })
        assert rv.status_code == 200
        refresh_token = rv.get_json()["refresh_token"]

        # Gunakan refresh token
        rv2 = client.post(
            "/api/v1/auth/refresh",
            headers={"Authorization": f"Bearer {refresh_token}"},
        )
        assert rv2.status_code == 200
        assert "access_token" in rv2.get_json()

    def test_refresh_with_access_token_fails(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.post("/api/v1/auth/refresh", headers=headers)
        assert rv.status_code == 422  # JWT Extended: wrong token type


class TestAuthLogout:
    def test_logout_success(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.post("/api/v1/auth/logout", headers=headers)
        assert rv.status_code == 200
        assert "Logged out" in rv.get_json()["message"]

    def test_logout_requires_token(self, client):
        rv = client.post("/api/v1/auth/logout")
        assert rv.status_code == 401
