"""Job store para recon assincrono."""

import uuid
from datetime import datetime
from typing import Any, Optional

_jobs: dict[str, dict] = {}


def create_job(domain: str) -> str:
    """Cria job e retorna ID."""
    job_id = str(uuid.uuid4())[:8]
    _jobs[job_id] = {
        "id": job_id,
        "domain": domain,
        "status": "pending",
        "progress": 0,
        "result": None,
        "error": None,
        "created_at": datetime.utcnow().isoformat(),
    }
    return job_id


def update_job(job_id: str, status: str = None, progress: int = None, result: Any = None, error: str = None):
    """Atualiza status do job."""
    if job_id not in _jobs:
        return
    if status:
        _jobs[job_id]["status"] = status
    if progress is not None:
        _jobs[job_id]["progress"] = progress
    if result is not None:
        _jobs[job_id]["result"] = result
    if error is not None:
        _jobs[job_id]["error"] = error


def get_job(job_id: str) -> Optional[dict]:
    """Retorna job por ID."""
    return _jobs.get(job_id)
