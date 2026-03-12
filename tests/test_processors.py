"""Testes dos processadores."""

from datetime import datetime

from app.models.recon_models import AssetType, ReconRecord
from app.processors import build_timeline, normalize_records


def test_normalize_deduplicates_by_asset():
    """Deduplica por asset mantendo o mais antigo."""
    records = [
        ReconRecord(source="a", asset="dev.example.com", discovered_at=datetime(2019, 1, 1)),
        ReconRecord(source="b", asset="dev.example.com", discovered_at=datetime(2018, 1, 1)),
    ]
    result = normalize_records(records)
    assert len(result) == 1
    assert result[0].discovered_at.year == 2018


def test_normalize_sorts_by_date():
    """Ordena por discovered_at."""
    records = [
        ReconRecord(source="a", asset="c.example.com", discovered_at=datetime(2020, 1, 1)),
        ReconRecord(source="a", asset="a.example.com", discovered_at=datetime(2018, 1, 1)),
        ReconRecord(source="a", asset="b.example.com", discovered_at=datetime(2019, 1, 1)),
    ]
    result = normalize_records(records)
    assert [r.asset for r in result] == ["a.example.com", "b.example.com", "c.example.com"]


def test_build_timeline_groups_by_year(sample_records):
    """Agrupa assets por ano."""
    normalized = normalize_records(sample_records)
    timeline = build_timeline(normalized)

    assert "2017" in timeline
    assert "dev.example.com" in timeline["2017"]
    assert "2020" in timeline
    assert "api.example.com" in timeline["2020"]
    assert "2019" in timeline
    assert "staging.example.com" in timeline["2019"]


def test_build_timeline_sorts_assets(sample_records):
    """Assets dentro de cada ano estão ordenados."""
    normalized = normalize_records(sample_records)
    timeline = build_timeline(normalized)

    for year, assets in timeline.items():
        assert assets == sorted(assets)
