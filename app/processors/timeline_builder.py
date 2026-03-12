"""Construtor de timeline por ano."""

from collections import defaultdict

from app.models.recon_models import ReconRecord


def build_timeline(records: list[ReconRecord]) -> dict[str, list[str]]:
    """
    Agrupa assets por ano de descoberta.

    Args:
        records: Lista de registros normalizados

    Returns:
        Dict {ano: [asset1, asset2, ...]} ordenado por ano
    """
    by_year: dict[str, list[str]] = defaultdict(list)
    seen_per_year: dict[str, set[str]] = defaultdict(set)

    for rec in records:
        year = _extract_year(rec)
        asset = rec.asset

        if asset in seen_per_year[year]:
            continue
        seen_per_year[year].add(asset)
        by_year[year].append(asset)

    result = {}
    for year in sorted(by_year.keys()):
        result[year] = sorted(by_year[year])

    return result


def _extract_year(rec: ReconRecord) -> str:
    """Extrai ano do registro. Se sem data, usa 'unknown'."""
    if rec.discovered_at:
        return str(rec.discovered_at.year)
    return "unknown"
