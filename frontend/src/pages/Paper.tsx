import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api } from "../api";

const inr = (n: number) => `₹${n.toLocaleString("en-IN")}`;

// Paper-trading sandbox: practise the engine's calls with fake money.
export function Paper({ onSelect }: { onSelect: (symbol: string) => void }) {
  const qc = useQueryClient();
  const [symbol, setSymbol] = useState("");
  const [qty, setQty] = useState(0);
  const [err, setErr] = useState<string | null>(null);

  const summary = useQuery({ queryKey: ["paper"], queryFn: api.paper });
  const trades = useQuery({ queryKey: ["paper-trades"], queryFn: api.paperTrades });

  const invalidate = () => {
    qc.invalidateQueries({ queryKey: ["paper"] });
    qc.invalidateQueries({ queryKey: ["paper-trades"] });
  };
  const order = useMutation({
    mutationFn: ({ side }: { side: "BUY" | "SELL" }) =>
      api.paperOrder(symbol.trim().toUpperCase(), side, qty),
    onSuccess: () => {
      setErr(null);
      setQty(0);
      invalidate();
    },
    onError: (e: Error) => setErr(e.message),
  });
  const reset = useMutation({
    mutationFn: () => api.paperReset(100000),
    onSuccess: invalidate,
  });

  const s = summary.data;
  const canOrder = symbol.trim() && qty > 0;

  return (
    <div>
      <div className="row-between">
        <h2 style={{ margin: 0 }}>Paper Trading</h2>
        <button className="tab" onClick={() => reset.mutate()}>
          Reset to ₹1,00,000
        </button>
      </div>
      <p className="muted">Fake money. Orders fill at the latest price. Practise risk-free.</p>

      {s && (
        <div className="cards-row" style={{ marginTop: 8 }}>
          <div className="card stat">
            <span className="muted">Equity</span>
            <strong>{inr(s.equity)}</strong>
          </div>
          <div className="card stat">
            <span className="muted">Cash</span>
            <strong>{inr(s.cash)}</strong>
          </div>
          <div className="card stat">
            <span className="muted">Total return</span>
            <strong className={s.total_return_pct >= 0 ? "pos" : "neg"}>
              {s.total_return_pct}% · realised {inr(s.realized_pnl)}
            </strong>
          </div>
        </div>
      )}

      <div className="card holding-form" style={{ marginTop: 16 }}>
        <input
          placeholder="Symbol (TCS.NS)"
          value={symbol}
          onChange={(e) => setSymbol(e.target.value.toUpperCase())}
        />
        <input
          type="number"
          step="any"
          placeholder="Qty"
          value={qty || ""}
          onChange={(e) => setQty(Number(e.target.value))}
        />
        <button
          disabled={!canOrder || order.isPending}
          style={{ background: "#26a69a", color: "#0f1117", borderRadius: 8, padding: "7px 16px" }}
          onClick={() => order.mutate({ side: "BUY" })}
        >
          Buy
        </button>
        <button
          disabled={!canOrder || order.isPending}
          style={{ background: "#ef5350", color: "#0f1117", borderRadius: 8, padding: "7px 16px" }}
          onClick={() => order.mutate({ side: "SELL" })}
        >
          Sell
        </button>
        {err && <span className="err">{err}</span>}
      </div>

      <section className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Open positions</h3>
        <table className="tbl">
          <thead>
            <tr>
              <th>Symbol</th>
              <th className="num">Qty</th>
              <th className="num">Avg cost</th>
              <th className="num">Price</th>
              <th className="num">Value</th>
              <th className="num">Unrealised P&L</th>
            </tr>
          </thead>
          <tbody>
            {(s?.positions ?? []).map((p) => {
              const up = (p.unrealized_pnl ?? 0) >= 0;
              return (
                <tr key={p.symbol} className="clickable" onClick={() => onSelect(p.symbol)}>
                  <td>
                    <strong>{p.symbol.replace(".NS", "")}</strong>
                  </td>
                  <td className="num">{p.quantity}</td>
                  <td className="num">{inr(p.avg_cost)}</td>
                  <td className="num">{p.current_price != null ? inr(p.current_price) : "—"}</td>
                  <td className="num">{p.market_value != null ? inr(p.market_value) : "—"}</td>
                  <td className={`num ${up ? "pos" : "neg"}`}>
                    {p.unrealized_pnl != null ? inr(p.unrealized_pnl) : "—"}
                  </td>
                </tr>
              );
            })}
            {s?.positions.length === 0 && (
              <tr>
                <td colSpan={6} className="muted">
                  No open positions. Place a buy order above.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>

      <section className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Trade log</h3>
        <table className="tbl">
          <thead>
            <tr>
              <th>Time</th>
              <th>Symbol</th>
              <th>Side</th>
              <th className="num">Qty</th>
              <th className="num">Price</th>
              <th className="num">Realised P&L</th>
            </tr>
          </thead>
          <tbody>
            {(trades.data ?? []).map((t) => (
              <tr key={t.id}>
                <td className="muted">{new Date(t.traded_at).toLocaleString("en-IN")}</td>
                <td>{t.symbol.replace(".NS", "")}</td>
                <td className={t.side === "BUY" ? "pos" : "neg"}>{t.side}</td>
                <td className="num">{t.quantity}</td>
                <td className="num">{inr(t.price)}</td>
                <td className="num">{t.side === "SELL" ? inr(t.realized_pnl) : "—"}</td>
              </tr>
            ))}
            {trades.data?.length === 0 && (
              <tr>
                <td colSpan={6} className="muted">
                  No trades yet.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
