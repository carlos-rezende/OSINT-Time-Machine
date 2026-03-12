"""GitHub Collector - busca menções ao domínio em repositórios."""

import re
from datetime import datetime

import httpx

from app.config import GITHUB_TOKEN
from app.models.recon_models import AssetType, ReconRecord

GITHUB_SEARCH_URL = "https://api.github.com/search/code"


async def collect_github(domain: str, limit: int = 30) -> list[ReconRecord]:
    """
    Busca menções ao domínio em código público no GitHub.

    Pode revelar: internal endpoints, staging servers, api keys em configs.

    Args:
        domain: Domínio alvo
        limit: Máximo de resultados (API limita a 100 por página)

    Returns:
        Lista de ReconRecords com subdomínios/URLs encontrados
    """
    records: list[ReconRecord] = []
    seen: set[str] = set()

    query = f'"{domain}"'
    headers = {"Accept": "application/vnd.github.v3+json"}
    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(
                GITHUB_SEARCH_URL,
                params={"q": query, "per_page": min(limit, 30)},
                headers=headers,
            )
            response.raise_for_status()
            data = response.json()
        except (httpx.HTTPError, ValueError):
            return records

    items = data.get("items", [])
    if not items:
        return records

    pattern = re.compile(rf"([a-zA-Z0-9][-a-zA-Z0-9]*\.)?{re.escape(domain)}", re.I)

    for item in items:
        path = item.get("path", "")
        name = item.get("name", "")
        html_url = item.get("html_url", "")

        for text in [path, name, html_url]:
            for match in pattern.finditer(text):
                full_match = match.group(0)
                if full_match and _belongs_to_domain(full_match, domain):
                    if full_match not in seen:
                        seen.add(full_match)
                        records.append(
                            ReconRecord(
                                source="github",
                                asset=full_match,
                                asset_type=AssetType.SUBDOMAIN,
                                discovered_at=datetime.utcnow(),
                                metadata={"repo": item.get("repository", {}).get("full_name")},
                            )
                        )

    return records


def _belongs_to_domain(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")
