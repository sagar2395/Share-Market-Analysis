# Implementation State

> **Single source of truth for "where we are."** Read this at the start of every
> session; update it at the end of every working run. See `CLAUDE.md` §2–3.

**Last updated:** 2026-06-27
**Current phase:** Phase 1 (MVP) — **core delivered**; polishing into Phase 2.

---

## Snapshot
Trading horizon is **swing/positional (2 weeks–6 months), no intraday** — analysis runs
on **daily + weekly** timeframes. The app now has: a persistent **watchlist**, a manual
**portfolio with live P&L**, a **dashboard**, an **Analyze** screen (candles + volume +
EMA/Bollinger overlays + the "what am I looking at?" teaching panel + daily/weekly
toggle), **EOD ingestion** into a DuckDB history store (daily job + manual trigger), and
four indicators (EMA, RSI, MACD, Bollinger) each with a plain-language `explain()`.
Backend has 13 passing tests; frontend builds clean.

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

## In progress 🚧
- [ ] (none — Phase 1 core complete)

## Next up ▶️ (remaining Phase 1 polish → Phase 2)
1. **Symbol search UX:** wire `/api/market/search` to an autocomplete (currently the
   watchlist accepts a typed symbol; universe is the curated NSE list — expand it).
2. **More indicators on the teaching panel:** ADX/Supertrend/ATR (swing-friendly).
3. **Phase 2 — Screener & signals:** filter the universe by technical/fundamental
   criteria; signal tags on the watchlist; alerts. (See `PLAN.md` §7, order FROZEN.)

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
