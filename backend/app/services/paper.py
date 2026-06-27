"""Paper-trading sandbox — simulate trades at live prices, risk-free.

A single cash account. Buys/sells execute at the active provider's current price
(market order), positions track average cost, and realised P&L accrues on sells. Lets
the owner practise the engine's calls before risking real money. Separate from the real
portfolio (`services/portfolio.py`).
"""

from __future__ import annotations

from sqlalchemy import select

from app.data.registry import get_provider
from app.storage.db import session_scope
from app.storage.models import PaperAccount, PaperPosition, PaperTrade

DEFAULT_STARTING_CASH = 100_000.0


class PaperError(ValueError):
    """Raised on invalid orders (insufficient cash / shares)."""


def _get_account(s) -> PaperAccount:
    acct = s.scalar(select(PaperAccount).limit(1))
    if acct is None:
        acct = PaperAccount(
            starting_cash=DEFAULT_STARTING_CASH,
            cash=DEFAULT_STARTING_CASH,
            realized_pnl=0.0,
        )
        s.add(acct)
        s.flush()
    return acct


def order(symbol: str, side: str, quantity: float) -> dict:
    symbol = symbol.strip().upper()
    side = side.strip().upper()
    if side not in ("BUY", "SELL"):
        raise PaperError("side must be BUY or SELL")
    if quantity <= 0:
        raise PaperError("quantity must be positive")

    provider = get_provider()
    price = provider.get_quote(symbol).price
    name = next(
        (m.name for m in provider.search_symbols(symbol) if m.symbol.upper() == symbol), ""
    )

    with session_scope() as s:
        acct = _get_account(s)
        pos = s.scalar(select(PaperPosition).where(PaperPosition.symbol == symbol))
        value = quantity * price
        realized = 0.0

        if side == "BUY":
            if value > acct.cash + 1e-6:
                raise PaperError(
                    f"Insufficient cash: need ₹{value:,.2f}, have ₹{acct.cash:,.2f}"
                )
            acct.cash -= value
            if pos is None:
                s.add(PaperPosition(symbol=symbol, name=name, quantity=quantity, avg_cost=price))
            else:
                total = pos.quantity + quantity
                pos.avg_cost = (pos.avg_cost * pos.quantity + price * quantity) / total
                pos.quantity = total
        else:  # SELL
            if pos is None or pos.quantity < quantity - 1e-6:
                have = pos.quantity if pos else 0
                raise PaperError(f"Insufficient shares: trying to sell {quantity}, have {have}")
            realized = (price - pos.avg_cost) * quantity
            acct.cash += value
            acct.realized_pnl += realized
            pos.quantity -= quantity
            if pos.quantity <= 1e-6:
                s.delete(pos)

        s.add(
            PaperTrade(
                symbol=symbol, side=side, quantity=quantity, price=price, realized_pnl=realized
            )
        )
        return {"symbol": symbol, "side": side, "quantity": quantity, "price": price,
                "value": round(value, 2), "realized_pnl": round(realized, 2)}


def summary() -> dict:
    provider = get_provider()
    with session_scope() as s:
        acct = _get_account(s)
        positions = s.scalars(select(PaperPosition)).all()
        pos_rows = [
            {"symbol": p.symbol, "name": p.name, "quantity": p.quantity, "avg_cost": p.avg_cost}
            for p in positions
        ]
        cash, starting, realized = acct.cash, acct.starting_cash, acct.realized_pnl

    holdings_value = 0.0
    enriched = []
    for r in pos_rows:
        try:
            price = provider.get_quote(r["symbol"]).price
        except Exception:  # noqa: BLE001
            price = None
        mv = r["quantity"] * price if price is not None else None
        upnl = (price - r["avg_cost"]) * r["quantity"] if price is not None else None
        if mv is not None:
            holdings_value += mv
        enriched.append(
            {
                **r,
                "current_price": price,
                "market_value": round(mv, 2) if mv is not None else None,
                "unrealized_pnl": round(upnl, 2) if upnl is not None else None,
            }
        )

    equity = cash + holdings_value
    return {
        "starting_cash": round(starting, 2),
        "cash": round(cash, 2),
        "holdings_value": round(holdings_value, 2),
        "equity": round(equity, 2),
        "realized_pnl": round(realized, 2),
        "total_return_pct": round((equity - starting) / starting * 100, 2) if starting else 0.0,
        "positions": enriched,
    }


def recent_trades(limit: int = 50) -> list[dict]:
    with session_scope() as s:
        trades = s.scalars(
            select(PaperTrade).order_by(PaperTrade.traded_at.desc()).limit(limit)
        ).all()
        return [
            {
                "id": t.id,
                "symbol": t.symbol,
                "side": t.side,
                "quantity": t.quantity,
                "price": t.price,
                "realized_pnl": round(t.realized_pnl, 2),
                "traded_at": t.traded_at.isoformat(),
            }
            for t in trades
        ]


def reset(starting_cash: float = DEFAULT_STARTING_CASH) -> dict:
    with session_scope() as s:
        for p in s.scalars(select(PaperPosition)).all():
            s.delete(p)
        for t in s.scalars(select(PaperTrade)).all():
            s.delete(t)
        acct = _get_account(s)
        acct.starting_cash = starting_cash
        acct.cash = starting_cash
        acct.realized_pnl = 0.0
    return summary()
