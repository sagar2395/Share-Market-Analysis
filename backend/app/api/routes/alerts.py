"""Alerts endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services import alerts

router = APIRouter(prefix="/alerts", tags=["alerts"])


class AlertIn(BaseModel):
    symbol: str
    kind: str
    threshold: float | None = None
    target: str = ""
    note: str = ""


@router.get("")
def list_all() -> list[dict]:
    return alerts.list_alerts()


@router.get("/kinds")
def kinds() -> list[str]:
    return list(alerts.KINDS)


@router.post("")
def create(body: AlertIn) -> dict:
    try:
        return alerts.create(body.model_dump())
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/evaluate")
def evaluate() -> list[dict]:
    """Evaluate active alerts now; results include a ``newly_fired`` edge flag."""
    return alerts.evaluate()


@router.post("/{alert_id}/toggle")
def toggle(alert_id: int) -> dict:
    result = alerts.toggle(alert_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Alert not found")
    return result


@router.delete("/{alert_id}")
def delete(alert_id: int) -> dict:
    return {"removed": alerts.delete(alert_id)}
