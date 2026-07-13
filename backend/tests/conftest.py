"""
Pytest configuration and shared fixtures for TwinFi AI backend tests.
"""
import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def mock_db_connections():
    """Session-scoped fixture that mocks all database connections."""
    with patch("app.database.mongodb.connect_to_mongo", new_callable=AsyncMock), \
         patch("app.database.redis_client.connect_to_redis", new_callable=AsyncMock), \
         patch("app.database.mongodb.close_mongo_connection", new_callable=AsyncMock), \
         patch("app.database.redis_client.close_redis_connection", new_callable=AsyncMock):
        yield


@pytest.fixture(scope="session")
def app(mock_db_connections):
    """Create the FastAPI app instance with mocked connections."""
    from app.main import app as fastapi_app
    return fastapi_app


@pytest.fixture
def client(app):
    """Per-test FastAPI test client."""
    with TestClient(app) as c:
        yield c


@pytest.fixture
def mock_db_session():
    """Mock SQLAlchemy async session."""
    session = AsyncMock()
    session.execute = AsyncMock()
    session.add = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.flush = AsyncMock()
    return session
