"""
Smoke test: /api/health
Memastikan app berjalan dan endpoint dasar merespons.
"""


class TestHealthCheck:
    def test_health_returns_200(self, client):
        rv = client.get("/api/health")
        assert rv.status_code == 200

    def test_health_returns_ok_status(self, client):
        body = client.get("/api/health").get_json()
        assert body["status"] == "ok"

    def test_health_no_auth_required(self, client):
        """Health check harus bisa diakses tanpa token."""
        rv = client.get("/api/health")
        assert rv.status_code == 200

    def test_not_found_returns_404(self, client):
        rv = client.get("/api/v1/nonexistent-endpoint")
        assert rv.status_code == 404
