"""Detector de exposições - subdomínios sensíveis e abandonados."""

import re

from app.models.recon_models import ReconRecord


SENSITIVE_PATTERNS = [
    r"^(dev|staging|stage|test|qa|beta|alpha|uat|preprod|demo)\.?",
    r"\.(dev|staging|test|internal|admin|backup)\.?",
    r"(admin|internal|intranet|vpn|secure|api\-old)\.?",
]


def detect_exposures(records: list[ReconRecord], domain: str) -> list[str]:
    """
    Detecta possíveis exposições nos assets descobertos.

    MVP: detecta subdomínios com padrões sensíveis (dev, staging, admin, etc.)

    Args:
        records: Lista de registros normalizados
        domain: Domínio alvo

    Returns:
        Lista de mensagens de exposição detectadas
    """
    exposures: list[str] = []

    for rec in records:
        asset_lower = rec.asset.lower()

        for pattern in SENSITIVE_PATTERNS:
            if re.search(pattern, asset_lower):
                exposures.append(
                    f"Subdomínio sensível detectado: {rec.asset} (fonte: {rec.source})"
                )
                break

    return exposures
