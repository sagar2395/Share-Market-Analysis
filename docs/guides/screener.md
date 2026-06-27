# Screener

The **Screener** scans your whole tradable universe and ranks the best swing/positional
setups, so you find candidates instead of staring at charts one by one. It's powered by
the same [confluence engine](confluence-signal.md) as the Analyze badge.

## How to use it
1. Pick a **preset** (what kind of setup you're hunting):
   - **Trend-aligned longs** — weekly + daily both up (cleanest longs).
   - **Buy-the-dip** — uptrend with the daily pulled back into a buyable zone.
   - **Oversold / basing** — stretched down, possible bounce to watch.
   - **Actionable (buy-rated)** — anything the engine currently rates a buy.
   - **All (ranked by score)** — the whole universe, best setups first.
2. Drag **Min score** to hide weaker setups (e.g. show only 60+).
3. Read the table — it's sorted with the **highest score at the top**.
4. **Click any row** to open that stock in **Analyze** and study it before acting.

## Reading the table
| Column | Meaning |
|---|---|
| Setup | The confluence badge (see the [confluence guide](confluence-signal.md)). |
| Weekly / Daily | Trend on each timeframe (green up, red down). |
| Score | Setup quality 0–100 — use it to rank, not as a promise. |
| Action | buy / watch / hold / avoid. |

## Tips for your style
- Start your session here: run **Buy-the-dip** and **Trend-aligned** with min score ~60,
  then click into the top 2–3 names to confirm on the chart.
- The screen is **technical** for now (price/trend/momentum). **Fundamental filters**
  (valuation, quality) arrive with the Phase 3 fundamentals data.
- The universe is currently a curated set of large-caps; a fuller NSE list is on the
  backlog.
