# Implementation State

> **Single source of truth for "where we are."** Read this at the start of every
> session; update it at the end of every working run. See `CLAUDE.md` §2–3.

**Last updated:** 2026-06-27
**Current phase:** Phase 2 (Screener & signals) — **COMPLETE** (signals, confluence,
screener, paper trading, alerts, pattern recognition, watchlist tags). Ready for Phase 3.

---

## Snapshot
Trading horizon is **swing/positional (2 weeks–6 months), no intraday** — analysis runs
on **daily + weekly** timeframes. The app has: a persistent **watchlist** (with **inline
confluence tags**), a manual **portfolio with live P&L**, a **dashboard**, an **Analyze**
screen (candles + volume + EMA/Bollinger overlays + "what am I looking at?" teaching +
daily/weekly toggle + **confluence badge** + **candlestick patterns & support/resistance**),
a **Screener** (preset scans ranked by setup score), a **Paper-trading** sandbox, an
**Alerts** system (price/RSI/confluence conditions, edge-triggered, browser
notifications), **EOD ingestion** into DuckDB, four indicators with `explain()`, a
**confluence signal engine**, and **pattern detection**. Backend: 24 passing tests;
frontend builds clean.

---

## Done ✅
### Phase 0 (foundation)
- [x] `PLAN.md`, `CLAUDE.md`, docs skeleton, recommendations log.
- [x] Backend scaffold, provider abstraction, `SampleProvider` (offline) +
      `YFinanceProvider` + registry with auto-fallback.
- [x] Indicator engine v0 (EMA/RSI/MACD) with `explain()`; REST API; tests.
- [x] Frontend scaffold: candlestick chart + explanation panel.

### Phase 1 (MVP)
- [x] **Trading horizon corrected** to swing/positional (2wk–6mo); docs updated; intraday
      removed; daily+weekly timeframes only.
- [x] **Storage:** SQLite (SQLAlchemy) for state; **DuckDB** history store (`storage/`).
- [x] **Watchlist:** persistent add/remove/list + live quotes (`services/watchlist.py`,
      `/api/watchlist*`) + sidebar UI.
- [x] **Portfolio (manual):** holdings with weighted-average-in, target/stop/horizon,
      **live P&L + totals** (`services/portfolio.py`, `/api/portfolio*`) + UI page.
- [x] **Weekly timeframe:** providers serve `1wk` (sample resamples; yfinance native).
- [x] **Bollinger Bands** indicator with squeeze detection + `explain()`.
- [x] **Chart overlays:** EMA(20/50) lines, Bollinger bands, volume histogram;
      `/api/analysis/overlays`. Daily/Weekly toggle in UI.
- [x] **EOD ingestion → DuckDB** (`services/ingestion.py`) + APScheduler daily job
      (18:30 IST) + manual `/api/admin/ingest`.
- [x] **Dashboard:** portfolio totals + watchlist movers.
- [x] Tests for all of the above (13 total, passing). User guides for watchlist &
      portfolio added.

### Phase 2 (Screener & signals) — core
- [x] **Confluence signal engine** (`intelligence/signals/`): weekly+daily verdict with
      badge, action (buy/watch/hold/avoid), 0–100 score, reasons, summary. Long-only
      bias (bearish = "avoid"/stand aside). `/api/signal`.
- [x] **Confluence badge** on the Analyze screen (the owner-approved feature).
- [x] **Screener** (`services/screener.py`, `/api/screener`): presets (trend-aligned,
      buy-the-dip, oversold/basing, actionable, all) ranked by score + min-score filter;
      Screener UI page.
- [x] **Paper-trading sandbox** (`services/paper.py`, `/api/paper*`): simulated cash
      account, buy/sell at live price, avg-cost positions, realised + unrealised P&L,
      equity & return, trade log, reset; Paper UI page.
- [x] **Alerts** (`services/alerts.py`, `/api/alerts*`): price/RSI/confluence-action
      conditions, **edge-triggered** (fires on unmet→met), pause/resume/delete; Alerts UI
      page polls `/evaluate` each minute and raises **browser notifications**.
- [x] **Pattern recognition** (`intelligence/patterns/`): candlestick patterns (doji,
      hammer, shooting star, bull/bear engulfing) + nearest **support/resistance** with
      teaching text; `/api/analysis/patterns`; shown on Analyze.
- [x] **Watchlist inline confluence tags** (`/api/watchlist/signals`): each sidebar row
      shows its badge/score for at-a-glance triage.
- [x] Tests for signals/screener/paper/alerts/patterns (24 total, passing).

## In progress 🚧
- [ ] (none — Phase 2 COMPLETE)

## Next up ▶️ (Phase 3 — Fundamentals & correlation engine)
1. **Fundamental data + per-stock scorecard** (ratios, quality) + peer comparison;
   add fundamental filters to the screener.
2. **Correlation engine:** rolling correlation heatmap, sector-rotation map, macro-factor
   exposure (USD/INR, crude, India VIX), **FII/DII flow** dashboard, delivery % analysis.
3. **Options data:** PCR / OI / max-pain (Nifty & Bank Nifty).
   See `PLAN.md` §7 (order FROZEN).

### Backlog (nice-to-have, not blocking)
- Symbol-search autocomplete + fuller NSE universe (currently curated large-caps).
- More indicators (ADX/Supertrend/ATR) on the teaching panel.
- Auto stop/target on signals + "paper-buy this setup" button (see RECOMMENDATIONS).

## Decisions & gotchas 📌
- **Horizon:** owner does NOT day-trade; "short-term" = 2wk–6mo. No intraday/minute data
  or tick streaming anywhere in the design.
- **Network in sandbox:** market-data hosts blocked; built **offline-first** via
  `SampleProvider`. Locally, `yfinance` serves real NSE/BSE data automatically.
- **Two stores:** `data/app.sqlite` (state) + `data/history.duckdb` (OHLCV history),
  both under `SMA_DATA_DIR` (gitignored).
- **Scheduler:** disabled in tests via `SMA_ENABLE_SCHEDULER=false`. Uses Asia/Kolkata;
  wrapped in try/except so the app serves even if it can't start.
- **Provider quote for P&L:** uses last close from the active provider; fine for EOD/
  swing use. Intraday live price not needed.

## How to run (quick)
- Backend: `cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload` → http://127.0.0.1:8000/docs
- Frontend: `cd frontend && npm install && npm run dev` → http://127.0.0.1:5173
- Tests: `cd backend && pytest`
- Manual data pull: `POST /api/admin/ingest` (or wait for the 18:30 IST job).

See `docs/development.md` for details.
