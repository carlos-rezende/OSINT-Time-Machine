"""Testes de integração da API."""

from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    """Health check retorna 200."""
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_timeline_invalid_domain(client):
    """Domínio inválido retorna 400."""
    r = client.post("/recon/timeline", json={"domain": ""})
    assert r.status_code == 400

    r = client.post("/recon/timeline", json={"domain": "invalid"})
    assert r.status_code == 400


@patch("app.api.routes.run_recon", new_callable=AsyncMock)
def test_timeline_success(mock_run_recon, client):
    """Timeline válida retorna 200 e estrutura correta."""
    mock_run_recon.return_value = (
        {"2018": ["dev.example.com"], "2020": ["api.example.com"]},
        ["Subdomínio sensível: dev.example.com"],
    )

    r = client.post("/recon/timeline", json={"domain": "example.com"})
    assert r.status_code == 200
    data = r.json()
    assert data["domain"] == "example.com"
    assert "timeline" in data
    assert data["timeline"]["2018"] == ["dev.example.com"]
    assert "exposures" in data
    assert len(data["exposures"]) == 1
