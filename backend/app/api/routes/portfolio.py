"""Portfolio endpoints — manual holdings with live P&L."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.services import portfolio

router = APIRouter(prefix="/portfolio", tags=["portfolio"])


class HoldingIn(BaseModel):
    symbol: str
    quantity: float = Field(..., gt=0)
    avg_cost: float = Field(..., gt=0)
    name: str | None = None
    target_price: float | None = None
    stop_loss: float | None = None
    horizon: str = "swing"  # "swing" | "long"
    notes: str = ""


@router.get("")
def get_portfolio() -> dict:
    return portfolio.summary()


@router.post("")
def add_holding(body: HoldingIn) -> dict:
    return portfolio.add(body.model_dump())


@router.delete("/{holding_id}")
def remove_holding(holding_id: int) -> dict:
    return {"removed": portfolio.remove(holding_id)}
