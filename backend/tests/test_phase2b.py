"""Phase 2 (cont.) tests: patterns, alerts, watchlist signal tags."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.intelligence.patterns import detect
from app.main import app

client = TestClient(app)


def test_patterns_report() -> None:
    rep = detect("RELIANCE.NS")
    assert rep.price > 0
    # support below price, resistance above (when both present)
    if rep.support is not None and rep.resistance is not None:
        assert rep.support <= rep.price <= rep.resistance
    assert rep.summary and rep.caveat


def test_patterns_endpoint() -> None:
    r = client.get("/api/analysis/patterns", params={"symbol": "TCS.NS"})
    assert r.status_code == 200
    assert "patterns" in r.json()


def test_watchlist_signals() -> None:
    client.post("/api/watchlist", json={"symbol": "RELIANCE.NS"})
    sigs = client.get("/api/watchlist/signals").json()
    row = next(s for s in sigs if s["symbol"] == "RELIANCE.NS")
    assert row["action"] in {"buy", "watch", "hold", "avoid"}
    assert 0 <= row["score"] <= 100


def test_alert_crud_and_evaluate() -> None:
    # Price-above with a tiny threshold → should be met immediately.
    created = client.post(
        "/api/alerts",
        json={"symbol": "RELIANCE.NS", "kind": "price_above", "threshold": 1},
    ).json()
    aid = created["id"]
    assert created["description"]

    results = client.post("/api/alerts/evaluate").json()
    fired = next(r for r in results if r["id"] == aid)
    assert fired["met"] is True
    assert fired["newly_fired"] is True  # edge-triggered on first eval

    # Second evaluation: still met but no longer "newly fired".
    results2 = client.post("/api/alerts/evaluate").json()
    fired2 = next(r for r in results2 if r["id"] == aid)
    assert fired2["met"] is True and fired2["newly_fired"] is False

    # Toggle off → excluded from evaluation.
    client.post(f"/api/alerts/{aid}/toggle")
    assert all(r["id"] != aid for r in client.post("/api/alerts/evaluate").json())

    assert client.delete(f"/api/alerts/{aid}").json()["removed"] is True


def test_alert_invalid_kind() -> None:
    r = client.post("/api/alerts", json={"symbol": "X.NS", "kind": "nope"})
    assert r.status_code == 400


def test_alert_confluence_action() -> None:
    created = client.post(
        "/api/alerts",
        json={"symbol": "RELIANCE.NS", "kind": "confluence_action", "target": "buy"},
    ).json()
    results = client.post("/api/alerts/evaluate").json()
    assert any(r["id"] == created["id"] for r in results)
    client.delete(f"/api/alerts/{created['id']}")
