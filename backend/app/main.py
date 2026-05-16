"""
Flock API — Application Entrypoint.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.simulate import router as simulate_router
from app.api.v1.sip import router as sip_router
from app.api.v1.stocks import router as stocks_router
from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Probabilistic portfolio planning for Indian retail investors.",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """Liveness probe for monitoring and deployment health checks."""
    return {"status": "ok", "service": settings.APP_NAME, "version": settings.APP_VERSION}


# ── Route Registration ───────────────────────────────────
app.include_router(stocks_router, prefix=settings.API_V1_PREFIX)
app.include_router(simulate_router, prefix=settings.API_V1_PREFIX)
app.include_router(sip_router, prefix=settings.API_V1_PREFIX)

# ── Serve Frontend Static Files ──────────────────────────
frontend_dir = Path(__file__).resolve().parent.parent.parent / "frontend"
if frontend_dir.exists():
    app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
