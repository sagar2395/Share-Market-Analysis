"""Paper-trading endpoints."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services import paper

router = APIRouter(prefix="/paper", tags=["paper"])


class OrderIn(BaseModel):
    symbol: str
    side: str  # BUY | SELL
    quantity: float = Field(..., gt=0)


class ResetIn(BaseModel):
    starting_cash: float = Field(paper.DEFAULT_STARTING_CASH, gt=0)


@router.get("")
def get_summary() -> dict:
    return paper.summary()


@router.get("/trades")
def get_trades() -> list[dict]:
    return paper.recent_trades()


@router.post("/order")
def place_order(body: OrderIn) -> dict:
    try:
        result = paper.order(body.symbol, body.side, body.quantity)
    except paper.PaperError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"executed": result, "summary": paper.summary()}


@router.post("/reset")
def reset(body: ResetIn) -> dict:
    return paper.reset(body.starting_cash)
