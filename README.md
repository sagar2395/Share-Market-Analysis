# Share-Market-Analysis

A **personal** market analysis & decision-support tool for the **Indian market
(NSE/BSE)**, built for a short-term trader with a long-term sleeve. It finds and
screens stocks, analyses them (technical + fundamental), surfaces **correlations &
money-flow** a normal user can't see, gives **explainable** buy/sell/hold suggestions —
and **teaches you** what every chart and correlation means and what to do about it.

> Local-first web app: a Python (FastAPI) analysis backend + a React/TypeScript
> frontend, run on your own machine. Optional lightweight desktop wrapper later.
>
> ⚠️ **Not financial advice.** Every output is a probabilistic aid. You decide.

## Status
**Phase 2 complete.** The app now has: watchlist (with inline confluence tags), manual
portfolio with live P&L, dashboard, an Analyze screen (candles + volume + EMA/Bollinger
overlays + daily/weekly toggle + the **what-am-I-looking-at** teaching panel + **candlestick
patterns & support/resistance**), a **weekly+daily confluence signal badge**, a **screener**
(preset scans ranked by setup score), a **paper-trading sandbox**, an **alerts** system
(price/RSI/confluence, browser notifications), EOD ingestion into DuckDB, and four
explainable indicators. Trading horizon is **swing/positional (2 weeks–6 months), no
intraday**. Next: Phase 3 (fundamentals & correlation/FII-DII engine).
See [`docs/IMPLEMENTATION_STATE.md`](docs/IMPLEMENTATION_STATE.md) for live progress and
[`PLAN.md`](PLAN.md) for the full design and roadmap.

## Quick start
```bash
# Backend (terminal 1)
cd backend && pip install -e ".[dev]" && uvicorn app.main:app --reload   # :8000/docs

# Frontend (terminal 2)
cd frontend && npm install && npm run dev                                 # :5173
```
Full instructions: [`docs/guides/getting-started.md`](docs/guides/getting-started.md).

## Tech stack
Python · FastAPI · pandas/numpy · DuckDB+SQLite · React · TypeScript · Vite ·
TradingView Lightweight Charts. Extensible plugin architecture for indicators,
signals, and data providers (free yfinance now → Zerodha/Upstox later).

## Documentation
- [`PLAN.md`](PLAN.md) — design & roadmap (phases frozen)
- [`docs/`](docs/README.md) — architecture, development, state, recommendations
- [`docs/guides/`](docs/guides/README.md) — how to use each feature
- [`CLAUDE.md`](CLAUDE.md) — instructions for AI agents continuing this project
