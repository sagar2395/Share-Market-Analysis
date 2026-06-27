# Getting Started

How to run Share-Market-Analysis on your Mac and open it.

## What you need (one-time)
- **Python 3.11+** and **Node.js 20+** installed.
- A terminal.

## 1. Start the backend (the analysis engine)
```bash
cd backend
python3 -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
uvicorn app.main:app --reload
```
Leave this running. It serves data and analysis at `http://127.0.0.1:8000`.
You can browse the raw API anytime at **http://127.0.0.1:8000/docs**.

**Live vs offline data:**
- With internet, it uses **real NSE/BSE data** (via yfinance) by default.
- With no internet (or in a sandbox), it automatically falls back to built-in
  **sample data** so the app still works. To force sample data:
  `SMA_PROVIDER=sample uvicorn app.main:app --reload`.

## 2. Start the app (the screen you use)
Open a **second** terminal:
```bash
cd frontend
npm install
npm run dev
```
Now open **http://127.0.0.1:5173** in your browser.

## 3. Use it
- Pick a stock from the **Symbol** dropdown (e.g. `RELIANCE.NS`).
- The left panel shows the **candlestick chart**.
- The right panel — **"What am I looking at?"** — explains each indicator in plain
  English and tells you what it implies. See
  [Price Chart & Explanations](chart-and-explanations.md).

## If something's not working
- **Right panel says "Failed to load analysis":** the backend isn't running — check
  terminal 1 and confirm `http://127.0.0.1:8000/api/health` returns `"status":"ok"`.
- **Chart empty / "Failed to load price data":** same — backend not reachable, or the
  symbol has no data. Try `RELIANCE.NS`.
- **Want to confirm which data is live:** the header shows `data: yfinance` (real) or
  `data: sample` (offline).

## Where things are
- Roadmap & design: `PLAN.md`
- All feature guides: `docs/guides/`
- For developers: `docs/development.md`
