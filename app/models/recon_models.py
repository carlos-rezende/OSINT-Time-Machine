"""Modelos de dados para o pipeline OSINT."""

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    """Tipo de asset descoberto."""

    SUBDOMAIN = "subdomain"
    ENDPOINT = "endpoint"
    PATH = "path"
    CERTIFICATE = "certificate"


class ReconRecord(BaseModel):
    """Registro normalizado de reconhecimento OSINT."""

    source: str = Field(..., description="Fonte dos dados (crtsh, wayback, dns, github)")
    asset: str = Field(..., description="Asset descoberto (subdomínio, URL, etc.)")
    asset_type: AssetType = Field(default=AssetType.SUBDOMAIN)
    discovered_at: Optional[datetime] = Field(
        default=None, description="Data de descoberta quando disponível"
    )
    metadata: dict = Field(default_factory=dict, description="Dados extras da fonte")


class TimelineRequest(BaseModel):
    """Request para geração de timeline."""

    domain: str = Field(..., description="Domínio alvo (ex: example.com)")


class TimelineResponse(BaseModel):
    """Resposta com timeline e exposições."""

    domain: str
    timeline: dict[str, list[str]] = Field(
        default_factory=dict,
        description="Timeline por ano: {'2018': ['dev.example.com'], ...}",
    )
    exposures: list[str] = Field(
        default_factory=list,
        description="Possíveis exposições detectadas",
    )
