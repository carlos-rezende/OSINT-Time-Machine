"""OSINT Time Machine - FastAPI Application."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.middleware import RateLimitMiddleware

app = FastAPI(
    title="OSINT Time Machine",
    description="Reconstrói a evolução histórica do attack surface de um domínio",
    version="0.1.0",
)

app.include_router(router)
app.add_middleware(RateLimitMiddleware)

STATIC_DIR = Path(__file__).parent.parent / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/")
async def root():
    """Serve o frontend."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/sw.js")
async def service_worker():
    """Service Worker para PWA."""
    return FileResponse(STATIC_DIR / "sw.js", media_type="application/javascript")


@app.get("/health")
async def health():
    """Health check para monitoramento."""
    return {"status": "ok", "service": "OSINT Time Machine"}
