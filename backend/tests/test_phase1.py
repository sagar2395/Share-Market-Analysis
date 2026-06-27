"""Phase 1 tests: watchlist, portfolio, ingestion, weekly interval, overlays."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_watchlist_add_list_remove() -> None:
    assert client.post("/api/watchlist", json={"symbol": "RELIANCE.NS"}).json()["added"] is True
    # Idempotent: adding again doesn't duplicate.
    assert client.post("/api/watchlist", json={"symbol": "RELIANCE.NS"}).json()["added"] is False

    symbols = [i["symbol"] for i in client.get("/api/watchlist").json()]
    assert "RELIANCE.NS" in symbols

    quotes = client.get("/api/watchlist/quotes").json()
    assert any(q["symbol"] == "RELIANCE.NS" and q["price"] is not None for q in quotes)

    assert client.delete("/api/watchlist/RELIANCE.NS").json()["removed"] is True


def test_portfolio_pnl_and_averaging() -> None:
    client.post("/api/portfolio", json={"symbol": "TCS.NS", "quantity": 10, "avg_cost": 3000})
    # Average-in a second lot.
    client.post("/api/portfolio", json={"symbol": "TCS.NS", "quantity": 10, "avg_cost": 3200})

    summary = client.get("/api/portfolio").json()
    tcs = next(h for h in summary["holdings"] if h["symbol"] == "TCS.NS")
    assert tcs["quantity"] == 20
    assert tcs["avg_cost"] == 3100  # weighted average of the two lots
    assert tcs["current_price"] is not None
    assert tcs["pnl"] is not None
    assert "pnl_percent" in summary["totals"]

    # cleanup
    client.delete(f"/api/portfolio/{tcs['id']}")


def test_weekly_interval() -> None:
    r = client.get("/api/market/ohlcv", params={"symbol": "INFY.NS", "interval": "1wk", "lookback": 52})
    assert r.status_code == 200
    bars = r.json()["bars"]
    assert len(bars) == 52


def test_overlays() -> None:
    r = client.get("/api/analysis/overlays", params={"symbol": "INFY.NS", "keys": "ema,bollinger"})
    assert r.status_code == 200
    series = r.json()["series"]
    assert "ema.ema20" in series and "bollinger.upper" in series
    assert all("time" in p and "value" in p for p in series["ema.ema20"][:3])


def test_ingestion_then_history() -> None:
    client.post("/api/watchlist", json={"symbol": "SBIN.NS"})
    report = client.post("/api/admin/ingest").json()
    assert report["symbols"] >= 1
    assert report["rows_written"] > 0
    stats = client.get("/api/admin/history/stats").json()
    assert stats["rows"] > 0


def test_bollinger_explanation() -> None:
    r = client.get("/api/analysis/indicators", params={"symbol": "INFY.NS", "keys": "bollinger"})
    assert r.status_code == 200
    e = r.json()[0]
    assert e["indicator"] == "bollinger"
    assert e["reading"] and e["action"]
