"""
TwinFi AI – Backend Test Suite
==============================
Basic test stubs to validate the CI/CD pipeline.
Expand with full integration tests as the project matures.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def client():
    """Create a FastAPI test client with mocked database connections."""
    # Mock DB connections so tests don't need real infrastructure
    with patch("app.database.mongodb.connect_to_mongo", new_callable=AsyncMock), \
         patch("app.database.redis_client.connect_to_redis", new_callable=AsyncMock), \
         patch("app.database.mongodb.close_mongo_connection", new_callable=AsyncMock), \
         patch("app.database.redis_client.close_redis_connection", new_callable=AsyncMock):
        from app.main import app
        with TestClient(app) as c:
            yield c


# ── Health Check Tests ────────────────────────────────────────────────────────
class TestHealthCheck:
    def test_health_check_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_response_structure(self, client):
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
        assert "version" in data
        assert "environment" in data

    def test_health_check_includes_services(self, client):
        response = client.get("/health")
        data = response.json()
        assert "services" in data


# ── Auth Tests ────────────────────────────────────────────────────────────────
class TestAuthRoutes:
    def test_register_requires_body(self, client):
        response = client.post("/api/v1/auth/register", json={})
        assert response.status_code == 422  # Validation error

    def test_login_requires_credentials(self, client):
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_protected_routes_require_auth(self, client):
        """All protected endpoints must return 401 without a token."""
        protected_endpoints = [
            ("GET", "/api/v1/dna/"),
            ("GET", "/api/v1/twin/"),
            ("GET", "/api/v1/twin/assets"),
            ("GET", "/api/v1/twin/predictions"),
            ("GET", "/api/v1/transactions/"),
            ("GET", "/api/v1/coach/insights"),
        ]
        for method, url in protected_endpoints:
            if method == "GET":
                response = client.get(url)
            else:
                response = client.post(url, json={})
            assert response.status_code == 401, f"Expected 401 for {method} {url}, got {response.status_code}"


# ── OpenAPI Documentation Tests ───────────────────────────────────────────────
class TestDocumentation:
    def test_openapi_schema_accessible(self, client):
        response = client.get("/api/openapi.json")
        assert response.status_code == 200

    def test_swagger_ui_accessible(self, client):
        response = client.get("/api/docs")
        assert response.status_code == 200

    def test_all_routers_registered(self, client):
        """Verify all expected API prefixes are in the OpenAPI schema."""
        response = client.get("/api/openapi.json")
        schema = response.json()
        paths = list(schema.get("paths", {}).keys())

        expected_prefixes = ["/api/v1/auth", "/api/v1/dna", "/api/v1/twin", "/api/v1/coach", "/api/v1/transactions"]
        for prefix in expected_prefixes:
            found = any(p.startswith(prefix) for p in paths)
            assert found, f"No routes found with prefix: {prefix}"
