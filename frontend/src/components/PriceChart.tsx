import { useEffect, useRef } from "react";
import { createChart, ColorType, type IChartApi } from "lightweight-charts";
import type { Candles } from "../api";

// Candlestick chart powered by TradingView Lightweight Charts.
export function PriceChart({ candles }: { candles: Candles }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      height: 420,
      layout: { background: { type: ColorType.Solid, color: "#0f1117" }, textColor: "#cbd5e1" },
      grid: { vertLines: { color: "#1c2030" }, horzLines: { color: "#1c2030" } },
      timeScale: { borderColor: "#2a2f42" },
      rightPriceScale: { borderColor: "#2a2f42" },
    });
    chartRef.current = chart;

    const series = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    series.setData(
      candles.bars.map((b) => ({
        time: b.time.slice(0, 10),
        open: b.open,
        high: b.high,
        low: b.low,
        close: b.close,
      })),
    );
    chart.timeScale().fitContent();

    const onResize = () =>
      containerRef.current && chart.applyOptions({ width: containerRef.current.clientWidth });
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [candles]);

  return <div ref={containerRef} style={{ width: "100%" }} />;
}
