"""Normalizador de registros OSINT."""

from datetime import datetime

from app.models.recon_models import ReconRecord


def normalize_records(records: list[ReconRecord]) -> list[ReconRecord]:
    """
    Normaliza e deduplica registros de múltiplas fontes.

    - Remove duplicatas por asset
    - Mantém o registro com a data mais antiga (primeira descoberta)
    - Ordena por discovered_at

    Args:
        records: Lista de registros brutos dos coletores

    Returns:
        Lista normalizada e deduplicada
    """
    by_asset: dict[str, ReconRecord] = {}

    for rec in records:
        asset_key = rec.asset.lower().strip()

        if asset_key not in by_asset:
            by_asset[asset_key] = rec
            continue

        existing = by_asset[asset_key]
        if rec.discovered_at and existing.discovered_at:
            if rec.discovered_at < existing.discovered_at:
                by_asset[asset_key] = rec
        elif rec.discovered_at and not existing.discovered_at:
            by_asset[asset_key] = rec

    result = list(by_asset.values())
    far_future = datetime(9999, 12, 31)
    result.sort(key=lambda r: (r.discovered_at or far_future, r.asset))
    return result
