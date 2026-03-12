"""Fixtures pytest."""

from datetime import datetime

import pytest

from app.models.recon_models import AssetType, ReconRecord


@pytest.fixture
def sample_records() -> list[ReconRecord]:
    """Registros de exemplo para testes."""
    return [
        ReconRecord(
            source="crtsh",
            asset="dev.example.com",
            asset_type=AssetType.SUBDOMAIN,
            discovered_at=datetime(2018, 5, 1),
        ),
        ReconRecord(
            source="wayback",
            asset="dev.example.com",
            asset_type=AssetType.SUBDOMAIN,
            discovered_at=datetime(2017, 3, 15),
        ),
        ReconRecord(
            source="crtsh",
            asset="api.example.com",
            asset_type=AssetType.SUBDOMAIN,
            discovered_at=datetime(2020, 1, 10),
        ),
        ReconRecord(
            source="crtsh",
            asset="staging.example.com",
            asset_type=AssetType.SUBDOMAIN,
            discovered_at=datetime(2019, 6, 1),
        ),
    ]
