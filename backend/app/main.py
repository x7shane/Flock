"""
Flock API — Application Entrypoint.

Run with:
    uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings

app = FastAPI(
    title=settings.APP_NAME,
    description="Probabilistic portfolio planning for Indian retail investors.",
    version=settings.APP_VERSION,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
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
# TODO: Wire up v1 routers as they are built
# from app.api.v1 import stocks, simulate
# app.include_router(stocks.router, prefix=settings.API_V1_PREFIX)
# app.include_router(simulate.router, prefix=settings.API_V1_PREFIX)
