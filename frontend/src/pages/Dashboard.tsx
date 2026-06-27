import { useQuery } from "@tanstack/react-query";
import { api } from "../api";

// At-a-glance: portfolio totals + watchlist movers. Click a symbol to analyse it.
export function Dashboard({ onSelect }: { onSelect: (symbol: string) => void }) {
  const portfolio = useQuery({ queryKey: ["portfolio"], queryFn: api.portfolio });
  const quotes = useQuery({ queryKey: ["watchlist"], queryFn: api.watchlistQuotes });

  const totals = portfolio.data?.totals;
  const movers = [...(quotes.data ?? [])].sort(
    (a, b) => (b.change_percent ?? 0) - (a.change_percent ?? 0),
  );

  return (
    <div>
      <h2>Dashboard</h2>

      <div className="cards-row">
        <div className="card stat">
          <span className="muted">Invested</span>
          <strong>{totals ? `₹${totals.invested.toLocaleString("en-IN")}` : "—"}</strong>
        </div>
        <div className="card stat">
          <span className="muted">Market value</span>
          <strong>{totals ? `₹${totals.market_value.toLocaleString("en-IN")}` : "—"}</strong>
        </div>
        <div className="card stat">
          <span className="muted">Unrealised P&L</span>
          <strong className={totals && totals.pnl >= 0 ? "pos" : "neg"}>
            {totals ? `₹${totals.pnl.toLocaleString("en-IN")} (${totals.pnl_percent}%)` : "—"}
          </strong>
        </div>
      </div>

      <section className="card" style={{ marginTop: 16 }}>
        <h3 style={{ marginTop: 0 }}>Watchlist movers</h3>
        {quotes.isLoading && <p className="muted">Loading…</p>}
        <table className="tbl">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Name</th>
              <th className="num">Price</th>
              <th className="num">Change %</th>
            </tr>
          </thead>
          <tbody>
            {movers.map((q) => {
              const up = (q.change_percent ?? 0) >= 0;
              return (
                <tr key={q.symbol} className="clickable" onClick={() => onSelect(q.symbol)}>
                  <td>
                    <strong>{q.symbol.replace(".NS", "")}</strong>
                  </td>
                  <td className="muted">{q.name}</td>
                  <td className="num">{q.price != null ? `₹${q.price.toLocaleString("en-IN")}` : "—"}</td>
                  <td className={`num ${up ? "pos" : "neg"}`}>
                    {q.change_percent != null ? `${up ? "+" : ""}${q.change_percent}%` : "—"}
                  </td>
                </tr>
              );
            })}
            {movers.length === 0 && (
              <tr>
                <td colSpan={4} className="muted">
                  Add symbols to your watchlist to see them here.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </section>
    </div>
  );
}
