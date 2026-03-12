"""Configuração da aplicação."""

import os


def get_env(key: str, default: str = "") -> str:
    """Retorna variável de ambiente."""
    return os.getenv(key, default)


PORT = int(get_env("PORT", "5000"))
REDIS_URL = get_env("REDIS_URL")
GITHUB_TOKEN = get_env("GITHUB_TOKEN")
RATE_LIMIT = int(get_env("RATE_LIMIT", "10"))
