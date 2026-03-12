"""DNS Collector - resolucao de registros."""

import asyncio
from datetime import datetime
from typing import List, Optional

import dns.resolver

from app.models.recon_models import AssetType, ReconRecord


def _resolve_sync(host: str, rtype: str) -> Optional[str]:
    """Resolucao DNS sincrona (executar em thread)."""
    try:
        answers = dns.resolver.resolve(host, rtype, raise_on_no_answer=False)
        for rdata in answers:
            return str(rdata).split()[-1] if rtype == "MX" else str(rdata)
    except Exception:
        pass
    return None


async def collect_dns(domain: str, subdomains: Optional[List[str]] = None) -> list[ReconRecord]:
    """
    Resolve registros DNS para o dominio e subdominios.

    Coleta A, AAAA, MX, TXT, NS.
    """
    records: list[ReconRecord] = []
    hosts_to_resolve = [domain]
    if subdomains:
        hosts_to_resolve.extend(subdomains[:30])

    record_types = ["A", "AAAA", "MX", "TXT", "NS"]
    loop = asyncio.get_event_loop()

    for host in hosts_to_resolve:
        host = host.split(":")[0].lower()
        if not _belongs_to_domain(host, domain):
            continue

        for rtype in record_types:
            value = await loop.run_in_executor(
                None, lambda h=host, r=rtype: _resolve_sync(h, r)
            )
            if value:
                records.append(
                    ReconRecord(
                        source="dns",
                        asset=host,
                        asset_type=AssetType.SUBDOMAIN,
                        discovered_at=datetime.utcnow(),
                        metadata={"record_type": rtype, "value": value},
                    )
                )
                break

    return records


def _belongs_to_domain(host: str, domain: str) -> bool:
    return host == domain or host.endswith(f".{domain}")
