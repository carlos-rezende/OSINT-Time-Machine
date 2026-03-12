"""Agent Orchestrator - Pipeline OSINT."""

import asyncio

from app.collectors import collect_crtsh, collect_wayback, collect_dns, collect_github
from app.processors import build_timeline, normalize_records
from app.analyzers.exposure_detector import detect_exposures


async def run_recon(domain: str) -> tuple[dict[str, list[str]], list[str]]:
    """
    Executa o pipeline completo de reconhecimento OSINT.

    Fluxo:
    1. Coleta dados (crt.sh, wayback, dns, github)
    2. Normaliza e deduplica
    3. Constrói timeline por ano
    4. Detecta exposições

    Args:
        domain: Domínio alvo (ex: example.com)

    Returns:
        (timeline, exposures)
    """
    crtsh_task = collect_crtsh(domain)
    wayback_task = collect_wayback(domain)
    github_task = collect_github(domain, limit=20)

    crtsh_records, wayback_records, github_records = await asyncio.gather(
        crtsh_task, wayback_task, github_task
    )

    all_so_far = crtsh_records + wayback_records + github_records
    subdomains = list({r.asset for r in all_so_far if r.asset != domain})[:30]
    dns_records = await collect_dns(domain, subdomains)

    all_records = all_so_far + dns_records
    normalized = normalize_records(all_records)
    timeline = build_timeline(normalized)
    exposures = detect_exposures(normalized, domain)

    return timeline, exposures
