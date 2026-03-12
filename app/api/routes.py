"""Rotas da API FastAPI."""

from fastapi import APIRouter, BackgroundTasks, HTTPException

from app.agents.recon_agent import run_recon
from app.cache import get_cached, set_cached
from app.jobs import create_job, get_job, update_job
from app.models.recon_models import TimelineRequest, TimelineResponse

router = APIRouter(prefix="/recon", tags=["recon"])


async def _run_recon_background(job_id: str, domain: str):
    """Executa recon em background e atualiza job."""
    try:
        update_job(job_id, status="running", progress=25)
        timeline, exposures = await run_recon(domain)
        update_job(
            job_id,
            status="completed",
            progress=100,
            result={"domain": domain, "timeline": timeline, "exposures": exposures},
        )
    except Exception as e:
        update_job(job_id, status="failed", error=str(e))


@router.post("/timeline", response_model=TimelineResponse)
async def get_timeline(request: TimelineRequest, background_tasks: BackgroundTasks):
    """Gera Attack Surface Timeline. Usa cache para domínios recentes."""
    domain = request.domain.strip().lower()

    if not domain or "." not in domain:
        raise HTTPException(status_code=400, detail="Domínio inválido")

    cache_key = f"timeline:{domain}"
    cached = await get_cached(cache_key)
    if cached:
        return TimelineResponse(**cached)

    try:
        timeline, exposures = await run_recon(domain)
        result = TimelineResponse(
            domain=domain,
            timeline=timeline,
            exposures=exposures,
        )
        await set_cached(cache_key, result.model_dump())
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/timeline/async")
async def get_timeline_async(request: TimelineRequest, background_tasks: BackgroundTasks):
    """Inicia recon em background. Use GET /recon/jobs/{job_id} para obter resultado."""
    domain = request.domain.strip().lower()
    if not domain or "." not in domain:
        raise HTTPException(status_code=400, detail="Domínio inválido")

    job_id = create_job(domain)
    background_tasks.add_task(_run_recon_background, job_id, domain)
    return {"job_id": job_id, "status": "pending"}


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Retorna status e resultado do job."""
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job não encontrado")
    return job
