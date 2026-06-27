import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { api, type NewHolding } from "../api";

const EMPTY: NewHolding = { symbol: "", quantity: 0, avg_cost: 0, horizon: "swing" };

// Manual portfolio: add holdings (with optional target/stop), see live P&L.
export function Portfolio({ onSelect }: { onSelect: (symbol: string) => void }) {
  const qc = useQueryClient();
  const [form, setForm] = useState<NewHolding>(EMPTY);

  const summary = useQuery({ queryKey: ["portfolio"], queryFn: api.portfolio });
  const add = useMutation({
    mutationFn: (h: NewHolding) => api.portfolioAdd(h),
    onSuccess: () => {
      setForm(EMPTY);
      qc.invalidateQueries({ queryKey: ["portfolio"] });
    },
  });
  const remove = useMutation({
    mutationFn: (id: number) => api.portfolioRemove(id),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["portfolio"] }),
  });

  const totals = summary.data?.totals;

  return (
    <div>
      <h2>Portfolio</h2>

      <form
        className="card holding-form"
        onSubmit={(e) => {
          e.preventDefault();
          if (form.symbol && form.quantity > 0 && form.avg_cost > 0) add.mutate(form);
        }}
      >
        <input
          placeholder="Symbol (RELIANCE.NS)"
          value={form.symbol}
          onChange={(e) => setForm({ ...form, symbol: e.target.value.toUpperCase() })}
        />
        <input
          type="number"
          step="any"
          placeholder="Qty"
          value={form.quantity || ""}
          onChange={(e) => setForm({ ...form, quantity: Number(e.target.value) })}
        />
        <input
          type="number"
          step="any"
          placeholder="Avg cost ₹"
          value={form.avg_cost || ""}
          onChange={(e) => setForm({ ...form, avg_cost: Number(e.target.value) })}
        />
        <input
          type="number"
          step="any"
          placeholder="Target ₹ (opt)"
          value={form.target_price ?? ""}
          onChange={(e) => setForm({ ...form, target_price: Number(e.target.value) || null })}
        />
        <input
          type="number"
          step="any"
          placeholder="Stop ₹ (opt)"
          value={form.stop_loss ?? ""}
          onChange={(e) => setForm({ ...form, stop_loss: Number(e.target.value) || null })}
        />
        <select
          value={form.horizon}
          onChange={(e) => setForm({ ...form, horizon: e.target.value })}
        >
          <option value="swing">Swing (2wk–6mo)</option>
          <option value="long">Long-term</option>
        </select>
        <button type="submit">Add</button>
      </form>

      <section className="card" style={{ marginTop: 16 }}>
        <table className="tbl">
          <thead>
            <tr>
              <th>Symbol</th>
              <th>Horizon</th>
              <th className="num">Qty</th>
              <th className="num">Avg cost</th>
              <th className="num">Price</th>
              <th className="num">Invested</th>
              <th className="num">Value</th>
              <th className="num">P&L</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            {(summary.data?.holdings ?? []).map((h) => {
              const up = (h.pnl ?? 0) >= 0;
              return (
                <tr key={h.id}>
                  <td className="clickable" onClick={() => onSelect(h.symbol)}>
                    <strong>{h.symbol.replace(".NS", "")}</strong>
                  </td>
                  <td className="muted">{h.horizon}</td>
                  <td className="num">{h.quantity}</td>
                  <td className="num">₹{h.avg_cost.toLocaleString("en-IN")}</td>
                  <td className="num">
                    {h.current_price != null ? `₹${h.current_price.toLocaleString("en-IN")}` : "—"}
                  </td>
                  <td className="num">₹{h.invested.toLocaleString("en-IN")}</td>
                  <td className="num">
                    {h.market_value != null ? `₹${h.market_value.toLocaleString("en-IN")}` : "—"}
                  </td>
                  <td className={`num ${up ? "pos" : "neg"}`}>
                    {h.pnl != null ? `₹${h.pnl.toLocaleString("en-IN")} (${h.pnl_percent}%)` : "—"}
                  </td>
                  <td>
                    <button className="wl-del" onClick={() => remove.mutate(h.id)}>
                      ×
                    </button>
                  </td>
                </tr>
              );
            })}
            {summary.data?.holdings.length === 0 && (
              <tr>
                <td colSpan={9} className="muted">
                  No holdings yet. Add one above.
                </td>
              </tr>
            )}
          </tbody>
          {totals && summary.data!.holdings.length > 0 && (
            <tfoot>
              <tr>
                <td colSpan={5}>
                  <strong>Total</strong>
                </td>
                <td className="num">
                  <strong>₹{totals.invested.toLocaleString("en-IN")}</strong>
                </td>
                <td className="num">
                  <strong>₹{totals.market_value.toLocaleString("en-IN")}</strong>
                </td>
                <td className={`num ${totals.pnl >= 0 ? "pos" : "neg"}`}>
                  <strong>
                    ₹{totals.pnl.toLocaleString("en-IN")} ({totals.pnl_percent}%)
                  </strong>
                </td>
                <td></td>
              </tr>
            </tfoot>
          )}
        </table>
      </section>
    </div>
  );
}
