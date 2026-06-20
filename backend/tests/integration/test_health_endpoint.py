"""
tests/integration/test_health_endpoint.py — Health Endpoint Integration Test
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check_returns_200():
    """
    Test that GET /health endpoint returns 200 and healthy status.
    """
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
