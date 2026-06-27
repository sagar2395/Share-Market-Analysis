# Portfolio

Track what you hold and see **live profit/loss**. Entry is manual for now (broker
auto-sync comes in a later phase), which is ideal while the focus is analysis.

## Add a holding
Fill the form at the top of the **Portfolio** tab:
- **Symbol** (e.g. `RELIANCE.NS`), **Qty**, **Avg cost** — required.
- **Target ₹** and **Stop ₹** — optional, but recommended for swing trades so your plan
  is recorded with the position.
- **Horizon** — *Swing (2wk–6mo)* or *Long-term*, so you can tell your two sleeves apart.

Adding the **same symbol again averages it in**: quantities add up and the avg cost
becomes the weighted average of both lots — exactly like buying more of an existing
position.

## Read the table
| Column | Meaning |
|---|---|
| Price | Latest price from the data provider. |
| Invested | Qty × avg cost (what you put in). |
| Value | Qty × current price (what it's worth now). |
| **P&L** | Value − Invested, with % — green = profit, red = loss. |
| Total row | Portfolio-wide invested / value / P&L. |

Click a symbol to open it in **Analyze**.

## How this supports your decisions
- See at a glance which positions are working and which are near your **stop** or
  **target** — your cue to act.
- The **Dashboard** mirrors the totals so you get a one-glance health check.
- P&L uses end-of-day/last price, which suits a 2-week-to-6-month horizon (no need to
  watch tick-by-tick).

## Notes
- Holdings are stored locally in `data/app.sqlite` — private to your machine.
- Removing a holding (**×**) deletes it; there's no trade history yet (a trade journal
  is planned for a later phase).
