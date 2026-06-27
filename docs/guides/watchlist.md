# Watchlist

The watchlist (left sidebar, always visible) is your shortlist of stocks to track and
analyse. It persists between sessions.

## Add / remove
- **Add:** type a symbol in the box (NSE format, e.g. `WIPRO.NS`) and press **+**.
- **Remove:** click the **×** on a row.
- Each row shows the **last price** and **% change**; the list refreshes about once a
  minute. Green = up, red = down.

## Use it
- **Click any row** to jump straight to the **Analyze** screen for that stock.
- The same symbols feed the **Dashboard** ("watchlist movers", sorted by % change) and
  are included in the nightly **EOD data pull** so their history builds up over time.

## Tips for a swing/positional trader
- Keep it focused (10–20 names you'd actually trade in the next weeks/months).
- Add a stock here first, watch how it behaves and what the indicators say, *then*
  decide — rather than buying on impulse.

## Notes
- Symbols use the NSE suffix `.NS` (BSE uses `.BO`). The built-in universe is a curated
  set of large-caps for now; a fuller symbol search arrives in a later phase.
- Prices come from the active data provider (real via yfinance when online; sample data
  offline — the header shows which).
