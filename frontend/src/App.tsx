import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { PriceChart } from "./components/PriceChart";
import { ExplanationPanel } from "./components/ExplanationPanel";

const DEFAULT_SYMBOLS = [
  "RELIANCE.NS",
  "TCS.NS",
  "HDFCBANK.NS",
  "INFY.NS",
  "ICICIBANK.NS",
  "SBIN.NS",
  "TATAMOTORS.NS",
];

export default function App() {
  const [symbol, setSymbol] = useState("RELIANCE.NS");

  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const candles = useQuery({ queryKey: ["ohlcv", symbol], queryFn: () => api.ohlcv(symbol) });
  const indicators = useQuery({
    queryKey: ["indicators", symbol],
    queryFn: () => api.indicators(symbol),
  });

  return (
    <div className="app">
      <header>
        <h1>Share-Market-Analysis</h1>
        <div className="muted">
          Personal NSE/BSE analysis &amp; decision support
          {health.data && ` · data: ${health.data.provider} · v${health.data.version}`}
        </div>
      </header>

      <div className="toolbar">
        <label htmlFor="sym">Symbol</label>
        <select id="sym" value={symbol} onChange={(e) => setSymbol(e.target.value)}>
          {DEFAULT_SYMBOLS.map((s) => (
            <option key={s} value={s}>
              {s}
            </option>
          ))}
        </select>
      </div>

      <div className="grid">
        <section className="card">
          <h2>{symbol}</h2>
          {candles.isLoading && <p className="muted">Loading chart…</p>}
          {candles.isError && <p className="err">Failed to load price data.</p>}
          {candles.data && <PriceChart candles={candles.data} />}
        </section>

        <section>
          <h2>What am I looking at?</h2>
          {indicators.isLoading && <p className="muted">Reading the indicators…</p>}
          {indicators.isError && <p className="err">Failed to load analysis.</p>}
          {indicators.data && <ExplanationPanel items={indicators.data} />}
        </section>
      </div>

      <footer className="muted">
        Not financial advice. Signals are aids — you decide.
      </footer>
    </div>
  );
}
