import type { PriceUpdate } from "../types/api";
import { shortDate } from "../utils";
import { comparablePriceGroups } from "../utils/priceComparability";

const WIDTH = 640;
const HEIGHT = 180;
const PADDING = 28;

export function PriceTrendChart({ items }: { items: PriceUpdate[] }) {
  if (items.length < 2) return null;
  const groups = comparablePriceGroups(items).filter((group) => group.length >= 2);
  const plotted = groups.reduce((count, group) => count + group.length, 0);
  return <>
    {groups.map((group) => <div key={group[0].id}>
      <p className="muted">{group[0].commodity.name} · {group[0].market.name} · {group[0].unit} · {group[0].bag_size} · {group[0].commodity_type}</p>
      <ComparableTrendChart items={group} />
    </div>)}
    {plotted < items.length && <p className="muted">Not enough comparable records.</p>}
  </>;
}

function ComparableTrendChart({ items }: { items: PriceUpdate[] }) {
  const points = items.map((item) => {
    const low = Number(item.price_low);
    const high = Number(item.price_high);
    const average = item.average_price !== null && item.average_price !== undefined ? Number(item.average_price) : (low + high) / 2;
    return { x: new Date(item.update_date_time).getTime(), y: average, low, high, date: item.update_date_time };
  });

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const point of points) {
    minX = Math.min(minX, point.x); maxX = Math.max(maxX, point.x);
    minY = Math.min(minY, point.low); maxY = Math.max(maxY, point.high);
  }

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
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-label="Price trend over time" preserveAspectRatio="none">
        <polygon className="trend-band" points={bandPoints} />
        <path className="trend-line" d={linePath} fill="none" />
        {points.map((p, i) => <circle key={i} className="trend-dot" cx={scaleX(p.x)} cy={scaleY(p.y)} r={3} />)}
      </svg>
      <div className="trend-chart-labels">
        <span>{shortDate(first.date)}</span>
        <span className="muted">Shaded band shows the daily low–high range; the line tracks the average.</span>
        <span>{shortDate(last.date)}</span>
      </div>
    </div>
  );
}
