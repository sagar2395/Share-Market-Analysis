import type { Explanation, Stance } from "../api";

// The "what am I looking at?" teaching panel — renders plain-language explanations
// (reading / action / caveat) for each indicator. This is the learning layer (PLAN §6d).
const STANCE_COLOR: Record<Stance, string> = {
  bullish: "#26a69a",
  bearish: "#ef5350",
  neutral: "#94a3b8",
};

export function ExplanationPanel({ items }: { items: Explanation[] }) {
  return (
    <div style={{ display: "grid", gap: 12 }}>
      {items.map((e) => (
        <div key={e.indicator} className="card">
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span
              style={{
                background: STANCE_COLOR[e.stance],
                color: "#0f1117",
                borderRadius: 6,
                padding: "2px 8px",
                fontSize: 12,
                fontWeight: 700,
                textTransform: "uppercase",
              }}
            >
              {e.stance}
            </span>
            <strong>{e.title}</strong>
          </div>
          <p className="muted" style={{ margin: "6px 0 8px" }}>
            {e.summary}
          </p>
          <p>
            <strong>What it's saying now:</strong> {e.reading}
          </p>
          <p>
            <strong>What to do:</strong> {e.action}
          </p>
          {e.caveat && (
            <p className="muted" style={{ fontStyle: "italic" }}>
              ⚠ {e.caveat}
            </p>
          )}
        </div>
      ))}
    </div>
  );
}
