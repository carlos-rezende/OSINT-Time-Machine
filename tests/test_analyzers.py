"""Testes dos analisadores."""

from datetime import datetime

from app.models.recon_models import AssetType, ReconRecord
from app.analyzers.exposure_detector import detect_exposures


def test_detect_exposures_staging():
    """Detecta subdomínio staging."""
    records = [
        ReconRecord(source="crtsh", asset="staging.example.com"),
    ]
    result = detect_exposures(records, "example.com")
    assert len(result) == 1
    assert "staging.example.com" in result[0]


def test_detect_exposures_dev():
    """Detecta subdomínio dev."""
    records = [
        ReconRecord(source="crtsh", asset="dev.example.com"),
    ]
    result = detect_exposures(records, "example.com")
    assert len(result) == 1


def test_detect_exposures_admin():
    """Detecta subdomínio admin."""
    records = [
        ReconRecord(source="wayback", asset="admin.example.com"),
    ]
    result = detect_exposures(records, "example.com")
    assert len(result) == 1


def test_detect_exposures_safe():
    """Não detecta subdomínios seguros."""
    records = [
        ReconRecord(source="crtsh", asset="www.example.com"),
        ReconRecord(source="crtsh", asset="api.example.com"),
    ]
    result = detect_exposures(records, "example.com")
    assert len(result) == 0
