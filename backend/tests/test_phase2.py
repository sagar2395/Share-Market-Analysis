"""Phase 2 tests: confluence signal, screener, paper trading."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.intelligence.signals import analyze
from app.main import app

client = TestClient(app)


def test_signal_shape() -> None:
    sig = analyze("RELIANCE.NS")
    assert sig.weekly_trend in {"up", "down", "flat"}
    assert sig.daily_trend in {"up", "down", "flat"}
    assert sig.action in {"buy", "watch", "hold", "avoid"}
    assert 0 <= sig.score <= 100
    assert sig.badge and sig.summary and sig.reasons


def test_signal_endpoint() -> None:
    r = client.get("/api/signal", params={"symbol": "TCS.NS"})
    assert r.status_code == 200
    assert r.json()["symbol"] == "TCS.NS"


def test_screener_presets_and_run() -> None:
    presets = client.get("/api/screener/presets").json()
    assert any(p["key"] == "trend_aligned" for p in presets)

    rows = client.get("/api/screener", params={"preset": "all"}).json()
    assert len(rows) > 0
    # Ranked by score descending.
    scores = [r["score"] for r in rows]
    assert scores == sorted(scores, reverse=True)
    # min_score filter respected.
    high = client.get("/api/screener", params={"preset": "all", "min_score": 60}).json()
    assert all(r["score"] >= 60 for r in high)


def test_paper_trading_flow() -> None:
    client.post("/api/paper/reset", json={"starting_cash": 100000})

    # Buy 10 of a stock; cash should fall, position appears.
    buy = client.post(
        "/api/paper/order", json={"symbol": "INFY.NS", "side": "BUY", "quantity": 10}
    )
    assert buy.status_code == 200
    summ = buy.json()["summary"]
    assert summ["cash"] < 100000
    assert any(p["symbol"] == "INFY.NS" and p["quantity"] == 10 for p in summ["positions"])

    # Oversell is rejected.
    bad = client.post(
        "/api/paper/order", json={"symbol": "INFY.NS", "side": "SELL", "quantity": 999}
    )
    assert bad.status_code == 400

    # Sell all; position closes and a trade is logged.
    sell = client.post(
        "/api/paper/order", json={"symbol": "INFY.NS", "side": "SELL", "quantity": 10}
    )
    assert sell.status_code == 200
    summ2 = sell.json()["summary"]
    assert all(p["symbol"] != "INFY.NS" for p in summ2["positions"])

    trades = client.get("/api/paper/trades").json()
    assert len(trades) >= 2


def test_paper_insufficient_cash() -> None:
    client.post("/api/paper/reset", json={"starting_cash": 100})
    r = client.post(
        "/api/paper/order", json={"symbol": "RELIANCE.NS", "side": "BUY", "quantity": 100}
    )
    assert r.status_code == 400
