import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { api } from "./api";
import { Watchlist } from "./components/Watchlist";
import { Dashboard } from "./pages/Dashboard";
import { Analyze } from "./pages/Analyze";
import { Portfolio } from "./pages/Portfolio";

type Tab = "dashboard" | "analyze" | "portfolio";

export default function App() {
  const [tab, setTab] = useState<Tab>("dashboard");
  const [symbol, setSymbol] = useState("RELIANCE.NS");
  const [interval, setInterval] = useState("1d");

  const health = useQuery({ queryKey: ["health"], queryFn: api.health });

  const select = (s: string) => {
    setSymbol(s);
    setTab("analyze");
  };

  return (
    <div className="shell">
      <header className="topbar">
        <div>
          <h1>Share-Market-Analysis</h1>
          <div className="muted">
            NSE/BSE swing &amp; positional analysis
            {health.data && ` · data: ${health.data.provider} · v${health.data.version}`}
          </div>
        </div>
        <nav className="tabs">
          {(["dashboard", "analyze", "portfolio"] as Tab[]).map((t) => (
            <button
              key={t}
              className={t === tab ? "tab active" : "tab"}
              onClick={() => setTab(t)}
            >
              {t[0].toUpperCase() + t.slice(1)}
            </button>
          ))}
        </nav>
      </header>

      <div className="body">
        <Watchlist selected={symbol} onSelect={select} />
        <main className="content">
          {tab === "dashboard" && <Dashboard onSelect={select} />}
          {tab === "analyze" && (
            <Analyze symbol={symbol} interval={interval} onInterval={setInterval} />
          )}
          {tab === "portfolio" && <Portfolio onSelect={select} />}
        </main>
      </div>

      <footer className="muted">Not financial advice. Signals are aids — you decide.</footer>
    </div>
  );
}
