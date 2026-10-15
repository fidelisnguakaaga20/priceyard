import type { PriceUpdate } from "../types/api";
import { money, shortDate } from "../utils";
import { groupComparablePrices, measurementLabel } from "../lib/priceSeries.mjs";

const WIDTH = 640;
const HEIGHT = 180;
const PADDING = 28;

export function PriceTrendChart({ items }: { items: PriceUpdate[] }) {
  if (items.length < 2) return null;
  const groups = groupComparablePrices(items).filter((group) => group.records.length >= 2);
  if (!groups.length) return <p className="muted">No two observations on this page have a matching market and recorded measurement for a trend.</p>;
  return <div>{groups.map((group) => <SeriesChart key={group.key} items={group.records} />)}</div>;
}

function SeriesChart({ items }: { items: PriceUpdate[] }) {
  const useAverage = items.every((item) => item.average_price !== null && Number.isFinite(Number(item.average_price)));
  const label = `${items[0].commodity.name} · ${items[0].market.name} · ${measurementLabel(items[0])}`;

  const points = items.map((item) => {
    const low = Number(item.price_low);
    const high = Number(item.price_high);
    const average = useAverage ? Number(item.average_price) : (low + high) / 2;
    return { x: new Date(item.update_date_time).getTime(), y: average, low, high, date: item.update_date_time };
  }).filter((point) => [point.x, point.y, point.low, point.high].every(Number.isFinite));
  if (points.length < 2) return null;

  const xs = points.map((p) => p.x);
  const minX = Math.min(...xs);
  const maxX = Math.max(...xs);
  const minY = Math.min(...points.map((p) => p.low));
  const maxY = Math.max(...points.map((p) => p.high));

  const scaleX = (x: number) => PADDING + (maxX === minX ? 0 : ((x - minX) / (maxX - minX)) * (WIDTH - PADDING * 2));
  const scaleY = (y: number) => HEIGHT - PADDING - (maxY === minY ? 0 : ((y - minY) / (maxY - minY)) * (HEIGHT - PADDING * 2));

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${scaleX(p.x).toFixed(1)} ${scaleY(p.y).toFixed(1)}`).join(" ");
  const bandPoints = [
    ...points.map((p) => `${scaleX(p.x).toFixed(1)},${scaleY(p.high).toFixed(1)}`),
    ...[...points].reverse().map((p) => `${scaleX(p.x).toFixed(1)},${scaleY(p.low).toFixed(1)}`),
  ].join(" ");

  const first = points[0];
  const last = points[points.length - 1];

  return (
    <div className="trend-chart">
      <h3>{label}</h3>
      <p className="muted">NGN range: {money(minY)} – {money(maxY)}</p>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label={`${label}: ${useAverage ? "recorded average" : "range midpoint"} over time`} preserveAspectRatio="none">
        <polygon className="trend-band" points={bandPoints} />
        <path className="trend-line" d={linePath} fill="none" />
        {points.map((p, i) => <circle key={i} className="trend-dot" cx={scaleX(p.x)} cy={scaleY(p.y)} r={3} />)}
      </svg>
      <div className="trend-chart-labels">
        <span>{shortDate(first.date)}</span>
        <span className="muted">Band: observed low–high range. Line: {useAverage ? "recorded average" : "range midpoint, not an observed average"}.</span>
        <span>{shortDate(last.date)}</span>
      </div>
    </div>
  );
}
