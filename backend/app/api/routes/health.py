"""Health & status endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app import __version__
from app.data.registry import get_provider

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict:
    """Liveness + which data provider is currently active."""
    provider = get_provider()
    return {
        "status": "ok",
        "version": __version__,
        "provider": provider.name,
    }
