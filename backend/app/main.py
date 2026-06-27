"""FastAPI application factory."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.routes import admin, analysis, health, market, portfolio, watchlist
from app.core.config import get_settings
from app.core.logging import get_logger, setup_logging
from app.core.scheduler import shutdown_scheduler, start_scheduler
from app.storage.db import init_db

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    init_db()
    if get_settings().enable_scheduler:
        try:
            start_scheduler()
        except Exception as exc:  # noqa: BLE001 — app should still serve if scheduler fails
            log.warning("Scheduler not started: %s", exc)
    yield
    shutdown_scheduler()


def create_app() -> FastAPI:
    setup_logging()
    settings = get_settings()

    app = FastAPI(
        title=settings.app_name,
        version=__version__,
        description="Personal NSE/BSE market analysis & decision-support tool.",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for module in (health, market, analysis, watchlist, portfolio, admin):
        app.include_router(module.router, prefix="/api")

    @app.get("/")
    def root() -> dict:
        return {"app": settings.app_name, "docs": "/docs", "health": "/api/health"}

    return app


app = create_app()
