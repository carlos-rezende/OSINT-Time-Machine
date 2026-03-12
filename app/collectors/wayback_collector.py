"""Wayback Machine Collector - web.archive.org CDX API."""

from datetime import datetime
from urllib.parse import urlparse

import httpx

from app.models.recon_models import AssetType, ReconRecord


WAYBACK_CDX_URL = "https://web.archive.org/cdx/search/cdx"


async def collect_wayback(domain: str, limit: int = 5000) -> list[ReconRecord]:
    """
    Coleta endpoints e subdomínios históricos via Wayback Machine CDX.

    Args:
        domain: Domínio alvo (ex: example.com)
        limit: Limite de resultados (default 5000)

    Returns:
        Lista de ReconRecords com URLs e subdomínios antigos
    """
    records: list[ReconRecord] = []
    seen: set[str] = set()

    params = {
        "url": f"*.{domain}/*",
        "output": "json",
        "limit": str(limit),
        "collapse": "urlkey",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.get(WAYBACK_CDX_URL, params=params)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError) as e:
            return records

    if not isinstance(data, list) or len(data) < 2:
        return records

    header = data[0]
    timestamp_idx = header.index("timestamp") if "timestamp" in header else 1
    original_idx = header.index("original") if "original" in header else 2

    for row in data[1:]:
        if len(row) <= max(timestamp_idx, original_idx):
            continue

        original_url = row[original_idx]
        timestamp_str = row[timestamp_idx]
        discovered_at = _parse_wayback_timestamp(timestamp_str)

        try:
            parsed = urlparse(original_url)
            host = parsed.netloc or parsed.path.split("/")[0]
        except Exception:
            continue

        if not host or not _belongs_to_domain(host, domain):
            continue

        if host in seen:
            continue
        seen.add(host)

        records.append(
            ReconRecord(
                source="wayback",
                asset=host,
                asset_type=AssetType.SUBDOMAIN,
                discovered_at=discovered_at,
                metadata={
                    "url": original_url,
                    "timestamp": timestamp_str,
                },
            )
        )

    return records


def _parse_wayback_timestamp(ts: str) -> datetime | None:
    """Parse timestamp CDX: 20180101120000 -> datetime."""
    if not ts or len(ts) < 8:
        return None
    try:
        return datetime(int(ts[:4]), int(ts[4:6]), int(ts[6:8]))
    except (ValueError, TypeError):
        return None


def _belongs_to_domain(host: str, domain: str) -> bool:
    """Verifica se host pertence ao domínio alvo."""
    host = host.lower().split(":")[0]
    return host == domain or host.endswith(f".{domain}")
