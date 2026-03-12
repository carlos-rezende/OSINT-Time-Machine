"""Certificate Transparency Collector - crt.sh."""

from datetime import datetime
from typing import Any

import httpx

from app.models.recon_models import AssetType, ReconRecord


CRTSH_URL = "https://crt.sh/?q=%25.{domain}&output=json"


async def collect_crtsh(domain: str) -> list[ReconRecord]:
    """
    Coleta subdomínios históricos via Certificate Transparency (crt.sh).

    Args:
        domain: Domínio alvo (ex: example.com)

    Returns:
        Lista de ReconRecords com subdomínios e datas de certificado
    """
    records: list[ReconRecord] = []
    seen: set[str] = set()

    url = CRTSH_URL.format(domain=domain)

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError):
            return records

    if not isinstance(data, list):
        return records

    for cert in data:
        if not isinstance(cert, dict):
            continue

        name_value = cert.get("name_value", "")
        if not name_value:
            continue

        # name_value pode conter múltiplos domínios separados por \n
        domains = [d.strip().lower() for d in name_value.split("\n") if d.strip()]

        # Parse da data - preferir entry_timestamp ou not_before
        discovered_at = _parse_crtsh_date(
            cert.get("entry_timestamp") or cert.get("not_before")
        )

        for subdomain in domains:
            if subdomain.startswith("*."):
                subdomain = subdomain[2:]

            if not _belongs_to_domain(subdomain, domain):
                continue

            asset = subdomain

            if asset in seen:
                continue
            seen.add(asset)

            records.append(
                ReconRecord(
                    source="crtsh",
                    asset=asset,
                    asset_type=AssetType.SUBDOMAIN,
                    discovered_at=discovered_at,
                    metadata={
                        "issuer": cert.get("issuer_name"),
                        "not_before": cert.get("not_before"),
                        "not_after": cert.get("not_after"),
                    },
                )
            )

    return records


def _parse_crtsh_date(value: Any) -> datetime | None:
    """Parse de data no formato crt.sh (ISO ou similar)."""
    if not value:
        return None
    try:
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except (ValueError, TypeError):
        pass
    return None


def _belongs_to_domain(subdomain: str, domain: str) -> bool:
    """Verifica se subdomínio pertence ao domínio alvo."""
    return subdomain == domain or subdomain.endswith(f".{domain}")
