"""
Integration tests: /api/v1/assets/*
Covers CRUD, permission enforcement, validation, soft delete, pagination.
"""
import json
import pytest


def post_json(client, url, data, headers=None):
    return client.post(url, data=json.dumps(data),
                       content_type="application/json", headers=headers or {})


def put_json(client, url, data, headers=None):
    return client.put(url, data=json.dumps(data),
                      content_type="application/json", headers=headers or {})


class TestListAssets:
    def test_list_requires_auth(self, client):
        rv = client.get("/api/v1/assets")
        assert rv.status_code == 401

    def test_list_returns_paginated_data(self, client, auth_headers, make_asset):
        make_asset(asset_tag="SRV-0001", serial_number="SN001")
        make_asset(asset_tag="SRV-0002", serial_number="SN002")
        _, headers = auth_headers
        rv = client.get("/api/v1/assets", headers=headers)
        assert rv.status_code == 200
        body = rv.get_json()
        assert "data"  in body
        assert "total" in body
        assert "pages" in body
        assert body["total"] >= 2

    def test_list_filter_by_status(self, client, auth_headers, make_asset):
        make_asset(asset_tag="ACTIVE-01", serial_number="A001", status="Active")
        make_asset(asset_tag="AVAIL-01",  serial_number="A002", status="Available")
        _, headers = auth_headers
        rv = client.get("/api/v1/assets?status=Active", headers=headers)
        assert rv.status_code == 200
        items = rv.get_json()["data"]
        assert all(a["status"] == "Active" for a in items)

    def test_list_search_by_asset_tag(self, client, auth_headers, make_asset):
        make_asset(asset_tag="SEARCH-001", serial_number="SC001")
        make_asset(asset_tag="OTHER-001",  serial_number="SC002")
        _, headers = auth_headers
        rv = client.get("/api/v1/assets?search=SEARCH", headers=headers)
        assert rv.status_code == 200
        items = rv.get_json()["data"]
        assert any("SEARCH" in a["asset_tag"] for a in items)

    def test_list_invalid_status_returns_400(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.get("/api/v1/assets?status=InvalidStatus", headers=headers)
        assert rv.status_code == 400

    def test_list_per_page_capped_at_100(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.get("/api/v1/assets?per_page=9999", headers=headers)
        assert rv.status_code == 200
        body = rv.get_json()
        assert body["per_page"] <= 100

    def test_list_soft_deleted_not_returned(self, client, auth_headers, make_asset, db_session):
        from datetime import datetime, timezone
        asset = make_asset(asset_tag="DELETED-01", serial_number="DEL001")
        asset.deleted_at = datetime.now(timezone.utc)
        db_session.flush()

        _, headers = auth_headers
        rv = client.get("/api/v1/assets", headers=headers)
        items = rv.get_json()["data"]
        assert not any(a["asset_tag"] == "DELETED-01" for a in items)


class TestGetAsset:
    def test_get_existing_asset(self, client, auth_headers, make_asset):
        asset = make_asset(asset_tag="GET-001", serial_number="G001")
        _, headers = auth_headers
        rv = client.get(f"/api/v1/assets/{asset.id}", headers=headers)
        assert rv.status_code == 200
        body = rv.get_json()
        assert body["asset_tag"] == "GET-001"

    def test_get_nonexistent_returns_404(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.get("/api/v1/assets/999999", headers=headers)
        assert rv.status_code == 404

    def test_get_soft_deleted_returns_404(self, client, auth_headers, make_asset, db_session):
        from datetime import datetime, timezone
        asset = make_asset(asset_tag="DEL-GET-01", serial_number="DG001")
        asset.deleted_at = datetime.now(timezone.utc)
        db_session.flush()

        _, headers = auth_headers
        rv = client.get(f"/api/v1/assets/{asset.id}", headers=headers)
        assert rv.status_code == 404

    def test_get_returns_network_relation(self, client, auth_headers, make_asset):
        asset = make_asset(asset_tag="NET-001", serial_number="N001")
        _, headers = auth_headers
        rv = client.get(f"/api/v1/assets/{asset.id}", headers=headers)
        body = rv.get_json()
        # network key harus ada (meski None)
        assert "network" in body


class TestCreateAsset:
    def test_create_success(self, client, auth_headers, make_model, make_location):
        model = make_model()
        location = make_location()
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "NEW-001",
            "serial_number": "NEW-SN-001",
            "model_id":      model.id,
            "location_id":   location.id,
            "status":        "Available",
        }, headers)
        assert rv.status_code == 201
        body = rv.get_json()
        assert body["asset_tag"] == "NEW-001"

    def test_create_duplicate_asset_tag_returns_409(self, client, auth_headers, make_asset, make_model, make_location):
        make_asset(asset_tag="DUP-001", serial_number="DUP-SN-001")
        model = make_model(name="ModelX")
        location = make_location(name="Loc2", code="LC-02")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "DUP-001",   # duplikat
            "serial_number": "UNIQUE-SN",
            "model_id":      model.id,
            "location_id":   location.id,
        }, headers)
        assert rv.status_code == 409

    def test_create_missing_required_fields_returns_422(self, client, auth_headers):
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag": "MISSING-FIELDS",
            # serial_number, model_id, location_id missing
        }, headers)
        assert rv.status_code == 422

    def test_create_invalid_asset_tag_format_returns_422(self, client, auth_headers, make_model, make_location):
        model = make_model(name="M2")
        location = make_location(name="L2", code="L2")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "INVALID TAG WITH SPACES",  # spasi tidak boleh
            "serial_number": "SN-INVALID",
            "model_id":      model.id,
            "location_id":   location.id,
        }, headers)
        assert rv.status_code == 422

    def test_create_invalid_model_id_returns_422(self, client, auth_headers, make_location):
        location = make_location(name="L3", code="L3")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "MODEL-INVALID",
            "serial_number": "SN-MI",
            "model_id":      99999,  # tidak exist
            "location_id":   location.id,
        }, headers)
        assert rv.status_code == 422

    def test_create_requires_permission(self, client, make_account, app):
        """Account tanpa asset:create tidak boleh buat asset."""
        limited = make_account(
            username="limited_create",
            password="Limit@123!",
            permissions=["asset:read"],  # hanya read, tidak ada create
        )
        with app.app_context():
            from flask_jwt_extended import create_access_token
            token = create_access_token(identity=str(limited.id))
        headers = {"Authorization": f"Bearer {token}"}
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag": "NO-PERM", "serial_number": "NP01",
            "model_id": 1, "location_id": 1,
        }, headers)
        assert rv.status_code == 403

    def test_create_strips_whitespace_from_strings(self, client, auth_headers, make_model, make_location):
        model = make_model(name="M3")
        location = make_location(name="L4", code="L4")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "  STRIP-001  ",
            "serial_number": "  STRIP-SN  ",
            "model_id":      model.id,
            "location_id":   location.id,
        }, headers)
        assert rv.status_code == 201
        body = rv.get_json()
        assert body["asset_tag"] == "STRIP-001"  # whitespace di-strip

    def test_create_mass_assignment_protection(self, client, auth_headers, make_model, make_location):
        """Field yang tidak ada di schema harus diabaikan."""
        model = make_model(name="M4")
        location = make_location(name="L5", code="L5")
        _, headers = auth_headers
        rv = post_json(client, "/api/v1/assets", {
            "asset_tag":     "MASS-001",
            "serial_number": "MASS-SN",
            "model_id":      model.id,
            "location_id":   location.id,
            "deleted_at":    "2020-01-01",  # field berbahaya — harus di-ignore
            "created_by":    99999,          # field berbahaya — harus di-ignore
        }, headers)
        assert rv.status_code == 201
        body = rv.get_json()
        assert body.get("deleted_at") is None


class TestUpdateAsset:
    def test_update_status(self, client, auth_headers, make_asset):
        asset = make_asset(asset_tag="UPD-001", serial_number="UPD-SN-001")
        _, headers = auth_headers
        rv = put_json(client, f"/api/v1/assets/{asset.id}", {
            "status": "Active"
        }, headers)
        assert rv.status_code == 200
        assert rv.get_json()["status"] == "Active"

    def test_update_nonexistent_returns_404(self, client, auth_headers):
        _, headers = auth_headers
        rv = put_json(client, "/api/v1/assets/999999", {"status": "Active"}, headers)
        assert rv.status_code == 404

    def test_update_duplicate_asset_tag_returns_409(self, client, auth_headers, make_asset):
        asset1 = make_asset(asset_tag="TAG-A", serial_number="SN-A")
        asset2 = make_asset(asset_tag="TAG-B", serial_number="SN-B")
        _, headers = auth_headers
        rv = put_json(client, f"/api/v1/assets/{asset2.id}", {
            "asset_tag": "TAG-A"  # sudah dipakai asset1
        }, headers)
        assert rv.status_code == 409

    def test_update_empty_body_returns_400(self, client, auth_headers, make_asset):
        asset = make_asset(asset_tag="EMPTY-UPD", serial_number="EU001")
        _, headers = auth_headers
        rv = put_json(client, f"/api/v1/assets/{asset.id}", {}, headers)
        assert rv.status_code == 400

    def test_update_only_allowed_fields(self, client, auth_headers, make_asset, db_session):
        """Field di luar UPDATABLE_FIELDS harus diabaikan."""
        asset = make_asset(asset_tag="ALLOW-001", serial_number="AL001")
        original_created_by = asset.created_by
        _, headers = auth_headers
        rv = put_json(client, f"/api/v1/assets/{asset.id}", {
            "status":     "Active",
            "created_by": 99999,  # tidak boleh diubah
        }, headers)
        assert rv.status_code == 200
        db_session.refresh(asset)
        # created_by tidak boleh berubah
        assert asset.created_by == original_created_by


class TestDeleteAsset:
    def test_delete_success_returns_200(self, client, auth_headers, make_asset):
        asset = make_asset(asset_tag="DEL-SUCCESS", serial_number="DS001")
        _, headers = auth_headers
        rv = client.delete(f"/api/v1/assets/{asset.id}", headers=headers)
        assert rv.status_code == 200

    def test_delete_is_soft_delete(self, client, auth_headers, make_asset, db_session):
        from app.models.asset import Asset
        asset = make_asset(asset_tag="SOFT-DEL", serial_number="SD001")
        asset_id = asset.id
        _, headers = auth_headers
        client.delete(f"/api/v1/assets/{asset_id}", headers=headers)

        # Asset masih ada di DB (soft delete)
        db_session.expire_all()
        found = db_session.get(Asset, asset_id)
        assert found is not None
        assert found.deleted_at is not None

    def test_delete_nonexistent_returns_404(self, client, auth_headers):
        _, headers = auth_headers
        rv = client.delete("/api/v1/assets/999999", headers=headers)
        assert rv.status_code == 404

    def test_delete_already_deleted_returns_404(self, client, auth_headers, make_asset, db_session):
        from datetime import datetime, timezone
        asset = make_asset(asset_tag="ALREADY-DEL", serial_number="AD001")
        asset.deleted_at = datetime.now(timezone.utc)
        db_session.flush()

        _, headers = auth_headers
        rv = client.delete(f"/api/v1/assets/{asset.id}", headers=headers)
        assert rv.status_code == 404
