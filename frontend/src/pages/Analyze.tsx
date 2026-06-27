import { useQuery } from "@tanstack/react-query";
import { api } from "../api";
import { PriceChart } from "../components/PriceChart";
import { ExplanationPanel } from "../components/ExplanationPanel";
import { ConfluenceBadge } from "../components/ConfluenceBadge";

const INTERVALS: { key: string; label: string }[] = [
  { key: "1d", label: "Daily" },
  { key: "1wk", label: "Weekly" },
];

// Analyse a single stock: chart + overlays + the "what am I looking at?" teaching panel.
export function Analyze({
  symbol,
  interval,
  onInterval,
}: {
  symbol: string;
  interval: string;
  onInterval: (i: string) => void;
}) {
  const candles = useQuery({
    queryKey: ["ohlcv", symbol, interval],
    queryFn: () => api.ohlcv(symbol, interval),
  });
  const overlays = useQuery({
    queryKey: ["overlays", symbol, interval],
    queryFn: () => api.overlays(symbol, interval),
  });
  const indicators = useQuery({
    queryKey: ["indicators", symbol, interval],
    queryFn: () => api.indicators(symbol, interval),
  });
  // Confluence is timeframe-independent (it reads weekly AND daily itself).
  const signal = useQuery({ queryKey: ["signal", symbol], queryFn: () => api.signal(symbol) });
  const patterns = useQuery({
    queryKey: ["patterns", symbol, interval],
    queryFn: () => api.patterns(symbol, interval),
  });

  return (
    <div>
      <div className="row-between">
        <h2 style={{ margin: 0 }}>{symbol}</h2>
        <div className="seg">
          {INTERVALS.map((i) => (
            <button
              key={i.key}
              className={i.key === interval ? "seg-btn active" : "seg-btn"}
              onClick={() => onInterval(i.key)}
            >
              {i.label}
            </button>
          ))}
        </div>
      </div>

      {signal.data && (
        <div style={{ marginBottom: 16 }}>
          <h3 style={{ margin: "0 0 8px" }}>Weekly + Daily confluence</h3>
          <ConfluenceBadge signal={signal.data} />
        </div>
      )}

      <div className="grid">
        <section className="card">
          {candles.isLoading && <p className="muted">Loading chart…</p>}
          {candles.isError && <p className="err">Failed to load price data.</p>}
          {candles.data && <PriceChart candles={candles.data} overlays={overlays.data} />}
          <p className="muted" style={{ marginTop: 8 }}>
            Orange/purple = EMA 20/50 · dashed blue = Bollinger bands · bars at bottom = volume.
          </p>
        </section>

        <section>
          {patterns.data && (
            <div className="card" style={{ marginBottom: 12 }}>
              <h3 style={{ marginTop: 0 }}>Patterns &amp; key levels</h3>
              <p>{patterns.data.summary}</p>
              {patterns.data.patterns.map((p) => (
                <p key={p.name}>
                  <strong className={`tf-${p.direction === "bullish" ? "up" : p.direction === "bearish" ? "down" : "flat"}`}>
                    {p.name}
                  </strong>{" "}
                  — {p.description}
                </p>
              ))}
              {patterns.data.caveat && (
                <p className="muted" style={{ fontStyle: "italic" }}>
                  ⚠ {patterns.data.caveat}
                </p>
              )}
            </div>
          )}

          <h3 style={{ marginTop: 0 }}>What am I looking at?</h3>
          {indicators.isLoading && <p className="muted">Reading the indicators…</p>}
          {indicators.isError && <p className="err">Failed to load analysis.</p>}
          {indicators.data && <ExplanationPanel items={indicators.data} />}
        </section>
      </div>
    </div>
  );
}
