import { useId } from "react";
import type { PriceUpdate } from "../types/api";
import { money } from "../utils";
import { priceEpoch, shortPriceDate } from "../utils/priceTime";
import { recordedPriceGroups } from "../utils/priceComparability";

const WIDTH = 640;
const HEIGHT = 180;
const PADDING = 28;

export function PriceTrendChart({ items }: { items: PriceUpdate[] }) {
  if (!items.length) return null;
  const groups = recordedPriceGroups(items);
  const plotted = groups.reduce((count, group) => count + group.items.length, 0);
  return <>
    {groups.map(({ items: group, comparable }) => <div key={group[0].id} className="history-price-series">
      <p className="muted">{group[0].commodity.name} · {group[0].market.name} · {group[0].unit || "Unit not recorded"} · {group[0].bag_size || "Size not recorded"} · {group[0].commodity_type || "Type not recorded"}</p>
      <RecordedTrendChart items={group} join={comparable && group.length >= 2} complete={comparable} />
    </div>)}
    {plotted < items.length && <p className="muted">Some records have an invalid price or an unconfirmed date/time and cannot be plotted. They remain in the history below.</p>}
  </>;
}

function RecordedTrendChart({ items, join, complete }: { items: PriceUpdate[]; join: boolean; complete: boolean }) {
  const chartId = useId();
  const points = items.map((item) => {
    const low = Number(item.price_low);
    const high = Number(item.price_high);
    const average = item.average_price !== null && item.average_price !== undefined ? Number(item.average_price) : (low + high) / 2;
    return { id: item.id, x: priceEpoch(item.update_date_time), y: average, low, high, date: item.update_date_time };
  });

  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const point of points) {
    minX = Math.min(minX, point.x); maxX = Math.max(maxX, point.x);
    minY = Math.min(minY, point.low); maxY = Math.max(maxY, point.high);
  }

  const scaleX = (x: number) => maxX === minX ? WIDTH / 2 : PADDING + ((x - minX) / (maxX - minX)) * (WIDTH - PADDING * 2);
  const scaleY = (y: number) => maxY === minY ? HEIGHT / 2 : HEIGHT - PADDING - ((y - minY) / (maxY - minY)) * (HEIGHT - PADDING * 2);

  const linePath = points.map((p, i) => `${i === 0 ? "M" : "L"} ${scaleX(p.x).toFixed(1)} ${scaleY(p.y).toFixed(1)}`).join(" ");
  const bandPoints = [
    ...points.map((p) => `${scaleX(p.x).toFixed(1)},${scaleY(p.high).toFixed(1)}`),
    ...[...points].reverse().map((p) => `${scaleX(p.x).toFixed(1)},${scaleY(p.low).toFixed(1)}`),
  ].join(" ");

  const first = points[0];
  const last = points[points.length - 1];

  return (
    <div className="trend-chart">
      <p className="trend-explanation">{join
        ? "The line shows the average; the shaded area shows each recorded low–high range."
        : complete ? "One recorded price. A trend line needs another matching record."
          : "Some measurement or type details were not recorded. Each price is shown separately; the points are not joined."}</p>
      <div className="trend-chart-scale"><span>High: {money(maxY)}</span><span>Low: {money(minY)}</span></div>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} role="img" aria-labelledby={`${chartId}-title ${chartId}-description`}>
        <title id={`${chartId}-title`}>{join ? "Price trend over time" : "Recorded prices over time"}</title>
        <desc id={`${chartId}-description`}>{items[0].commodity.name} at {items[0].market.name}. {points.length} recorded {points.length === 1 ? "price" : "prices"}, from {shortPriceDate(first.date)} to {shortPriceDate(last.date)}. {join ? "Only matching recorded measurements and types are connected." : "Separate markers show prices without asserting they are comparable."}</desc>
        {join && <><polygon className="trend-band" points={bandPoints} /><path className="trend-line" d={linePath} fill="none" /></>}
        {points.map((p) => <g key={p.id}>
          <title>{shortPriceDate(p.date)}: {money(p.low)} – {money(p.high)}</title>
          <line className="trend-range" x1={scaleX(p.x)} x2={scaleX(p.x)} y1={scaleY(p.low)} y2={scaleY(p.high)} />
          <circle className="trend-dot" cx={scaleX(p.x)} cy={scaleY(p.y)} r={3} />
        </g>)}
      </svg>
      <div className="trend-chart-labels">
        <span>{shortPriceDate(first.date)}</span>
        <span>{shortPriceDate(last.date)}</span>
      </div>
    </div>
  );
}
