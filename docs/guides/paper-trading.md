# Paper Trading

A **practice account with fake money.** Test the engine's calls and your own ideas with
zero risk before committing real capital — the best way to build confidence in a setup.

## How it works
- You start with **₹1,00,000** of pretend cash.
- **Buy** or **Sell** any symbol — orders fill instantly at the **latest price**.
- The app tracks your **positions** (with average cost), **cash**, **equity**
  (cash + holdings), **realised P&L** (locked in when you sell) and **unrealised P&L**
  (open positions), plus your **total return %**.
- Every fill is recorded in the **trade log**.
- Hit **Reset to ₹1,00,000** anytime to start fresh.

## Place an order
1. Go to the **Paper** tab.
2. Type a **Symbol** (e.g. `TCS.NS`) and a **Qty**.
3. Click **Buy** or **Sell**.
   - Buys are blocked if you don't have enough cash.
   - Sells are blocked if you don't hold enough shares.
   - The reason appears next to the buttons if an order is rejected.
4. Click a position row to jump to **Analyze** for that stock.

## How to get value from it
- **Validate the badge:** when the [confluence badge](confluence-signal.md) says
  "Buy-the-dip zone", paper-buy it and watch how it plays out over days/weeks. You'll
  learn which setups you trust.
- **Rehearse exits:** practise selling at your target or stop so the discipline is
  automatic when real money is on the line.
- **Compare to the real [Portfolio](portfolio.md):** paper is for experiments; the
  portfolio tab is for what you actually hold. They're kept completely separate.

## Notes
- It's a **simulator**: no brokerage/slippage/taxes are modelled, and fills are at the
  last price. Real trading has costs — treat paper results as optimistic.
- Everything is stored locally in `data/app.sqlite`, private to your machine.
- Broker integration (real orders via Zerodha/Upstox) is a later phase; this sandbox is
  the safe place to practise until then.
