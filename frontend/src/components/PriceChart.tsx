import { useEffect, useRef } from "react";
import { createChart, ColorType, LineStyle, type IChartApi } from "lightweight-charts";
import type { Candles, Overlays } from "../api";

// Colour per overlay series key (returned by /analysis/overlays as "<indicator>.<col>").
const OVERLAY_STYLE: Record<string, { color: string; dashed?: boolean }> = {
  "ema.ema20": { color: "#f5a623" },
  "ema.ema50": { color: "#9013fe" },
  "bollinger.upper": { color: "#4a90d9", dashed: true },
  "bollinger.mid": { color: "#6b7280", dashed: true },
  "bollinger.lower": { color: "#4a90d9", dashed: true },
};

// Candlestick chart with optional indicator line overlays.
export function PriceChart({ candles, overlays }: { candles: Candles; overlays?: Overlays }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      height: 440,
      layout: { background: { type: ColorType.Solid, color: "#0f1117" }, textColor: "#cbd5e1" },
      grid: { vertLines: { color: "#1c2030" }, horzLines: { color: "#1c2030" } },
      timeScale: { borderColor: "#2a2f42" },
      rightPriceScale: { borderColor: "#2a2f42" },
    });
    chartRef.current = chart;

    const candleSeries = chart.addCandlestickSeries({
      upColor: "#26a69a",
      downColor: "#ef5350",
      borderVisible: false,
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
    });
    candleSeries.setData(
      candles.bars.map((b) => ({
        time: b.time.slice(0, 10),
        open: b.open,
        high: b.high,
        low: b.low,
        close: b.close,
      })),
    );

    const volumeSeries = chart.addHistogramSeries({
      priceFormat: { type: "volume" },
      priceScaleId: "vol",
      color: "#2a3142",
    });
    chart.priceScale("vol").applyOptions({ scaleMargins: { top: 0.82, bottom: 0 } });
    volumeSeries.setData(
      candles.bars.map((b) => ({
        time: b.time.slice(0, 10),
        value: b.volume,
        color: b.close >= b.open ? "#1f4d45" : "#4d2330",
      })),
    );

    if (overlays) {
      for (const [key, points] of Object.entries(overlays.series)) {
        const style = OVERLAY_STYLE[key];
        if (!style) continue;
        const line = chart.addLineSeries({
          color: style.color,
          lineWidth: 2,
          lineStyle: style.dashed ? LineStyle.Dashed : LineStyle.Solid,
          priceLineVisible: false,
          lastValueVisible: false,
        });
        line.setData(
          points
            .filter((p) => p.value !== null)
            .map((p) => ({ time: p.time, value: p.value as number })),
        );
      }
    }

    chart.timeScale().fitContent();
    const onResize = () =>
      containerRef.current && chart.applyOptions({ width: containerRef.current.clientWidth });
    onResize();
    window.addEventListener("resize", onResize);
    return () => {
      window.removeEventListener("resize", onResize);
      chart.remove();
    };
  }, [candles, overlays]);

  return <div ref={containerRef} style={{ width: "100%" }} />;
}
