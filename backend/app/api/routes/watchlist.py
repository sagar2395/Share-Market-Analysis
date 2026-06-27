"""Watchlist endpoints."""

from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel

from app.services import watchlist

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


class SymbolIn(BaseModel):
    symbol: str


@router.get("")
def get_watchlist() -> list[dict]:
    return watchlist.list_items()


@router.get("/quotes")
def get_quotes() -> list[dict]:
    return watchlist.quotes()


@router.post("")
def add_symbol(body: SymbolIn) -> dict:
    return watchlist.add(body.symbol)


@router.delete("/{symbol}")
def remove_symbol(symbol: str) -> dict:
    return {"removed": watchlist.remove(symbol)}
