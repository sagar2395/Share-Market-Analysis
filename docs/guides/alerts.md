# Alerts

Get notified when something you care about happens, so you don't have to stare at
screens. Alerts are checked against current data every minute while the **Alerts** tab is
open, and they raise a **browser notification** the moment a condition is first met.

## Create an alert
1. Go to the **Alerts** tab (allow notifications when the browser asks).
2. Enter a **Symbol** (e.g. `RELIANCE.NS`).
3. Pick a **condition**:
   - **Price ≥ / ≤** a level — e.g. price hits your target or stop.
   - **RSI ≥ / ≤** a level — e.g. momentum gets overbought (≥70) or oversold (≤30).
   - **Confluence becomes** an action — fire when the weekly+daily verdict turns
     **buy** (e.g. a name enters a buy-the-dip / trend-aligned setup), or **avoid**, etc.
4. Set the level (or pick the action) and click **Add alert**.

## How firing works
Alerts are **edge-triggered**: one fires only when its condition flips from *not met* to
*met*, so you get a single notification per event — not a buzz every minute while it stays
true. The status column shows **watching**, **met**, or **paused**, plus the last time it
triggered.

## Manage
- **Pause/Resume** to mute an alert without deleting it.
- **×** to delete.
- Click a condition to jump to that stock in **Analyze**.

## Tips for your style
- Put a **Price ≤ stop** and **Price ≥ target** alert on every open position so you never
  miss an exit.
- Use **Confluence becomes buy** on watchlist names you'd trade *if* the setup lines up —
  the app tells you when it does.

## Notes
- Checking only runs while the **Alerts** tab is open (a background scheduler comes later).
- Notifications need browser permission; if you blocked it, re-enable in site settings.
- Alerts are stored locally in `data/app.sqlite`.
