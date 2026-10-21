import { useId, useLayoutEffect, useRef, useState } from "react";
import type { PriceUpdate } from "../types/api";
import { money } from "../utils";
import { priceEpoch, shortPriceDate } from "../utils/priceTime";
import { recordedPriceGroups } from "../utils/priceComparability";

const HEIGHT = 250;
const TOP = 18;
const BOTTOM = 54;
const dateTick = new Intl.DateTimeFormat("en-NG", {
  timeZone: "Africa/Lagos", day: "numeric", month: "short", year: "2-digit",
});

function SeriesHeading({ item, count }: { item: PriceUpdate; count: number }) {
  return <>
    <div className="trend-heading">
      <div><h2>{item.commodity.name}</h2><p>{item.market.name}</p></div>
      <span className="trend-record-count">{count} {count === 1 ? "record" : "records"}</span>
    </div>
    <p className="trend-specification">{item.unit || "Unit not recorded"} · {item.bag_size || "Size not recorded"} · {item.commodity_type || "Type not recorded"}</p>
  </>;
}

export function PriceTrendChart({ items }: { items: PriceUpdate[] }) {
  if (!items.length) return null;
  const groups = recordedPriceGroups(items);
  const plotted = groups.reduce((count, group) => count + group.items.length, 0);
  return <div className="history-trends">
    {groups.map(({ items: group, comparable }) => group.length === 1
      ? <section key={group[0].id} className="history-price-series history-single-price">
        <SeriesHeading item={group[0]} count={1} />
        <div className="single-price-details">
          <strong>{money(group[0].price_low)} – {money(group[0].price_high)}</strong>
          <time dateTime={group[0].update_date_time}>{shortPriceDate(group[0].update_date_time)}</time>
        </div>
        <p className="trend-explanation">One price recorded; no trend available yet.</p>
      </section>
      : <RecordedTrendChart key={group[0].id} items={group} complete={comparable} />)}
    {plotted < items.length && <p className="muted">Some records have an invalid price or an unconfirmed date/time and cannot be plotted. They remain in the history below.</p>}
  </div>;
}

function niceStep(value: number): number {
  const power = 10 ** Math.floor(Math.log10(value));
  const fraction = value / power;
  return (fraction <= 1 ? 1 : fraction <= 2 ? 2 : fraction <= 5 ? 5 : 10) * power;
}

function RecordedTrendChart({ items, complete }: { items: PriceUpdate[]; complete: boolean }) {
  const chartId = useId();
  const plotRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(640);
  const [selectedId, setSelectedId] = useState<number | null>(null);
  useLayoutEffect(() => {
    const element = plotRef.current;
    if (!element) return;
    const measure = () => setWidth(Math.max(240, Math.round(element.getBoundingClientRect().width)));
    measure();
    const observer = new ResizeObserver(measure);
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  const points = items.map((item) => ({
    id: item.id, x: priceEpoch(item.update_date_time), date: item.update_date_time,
    low: Number(item.price_low), high: Number(item.price_high),
    y: item.average_price == null ? (Number(item.price_low) + Number(item.price_high)) / 2 : Number(item.average_price),
    hasAverage: item.average_price != null,
  }));
  const first = points[0], last = points[points.length - 1];
  const sameDay = dateTick.format(first.x) === dateTick.format(last.x);
  const timeTick = new Intl.DateTimeFormat("en-NG", {
    timeZone: "Africa/Lagos", hour: "numeric", minute: "2-digit",
    ...(last.x - first.x < 60_000 ? { second: "2-digit" as const } : {}),
  });
  const join = complete && first.x < last.x;
  const selectedIndex = Math.max(0, selectedId === null ? points.length - 1 : points.findIndex((point) => point.id === selectedId));
  const selected = points[selectedIndex];
  let rawMin = Infinity, rawMax = -Infinity;
  for (const point of points) {
    rawMin = Math.min(rawMin, point.low); rawMax = Math.max(rawMax, point.high);
  }
  const padding = Math.max((rawMax - rawMin) * .08, rawMax === rawMin ? Math.max(rawMax * .05, 1) : .01);
  const step = niceStep((rawMax - rawMin + padding * 2) / 4);
  const minY = Math.max(0, Math.floor((rawMin - padding) / step) * step);
  const maxY = Math.max(minY + step, Math.ceil((rawMax + padding) / step) * step);
  const currencyTick = new Intl.NumberFormat("en-NG", {
    style: "currency", currency: "NGN", minimumFractionDigits: 0,
    maximumFractionDigits: step < 1 ? 2 : 0,
  });
  const yTicks = Array.from({ length: Math.round((maxY - minY) / step) + 1 }, (_, index) => minY + index * step);
  const left = Math.max(76, Math.min(116, currencyTick.format(maxY).length * 7 + 12));
  const right = width - 18;
  const bottom = HEIGHT - BOTTOM;
  const scaleX = (x: number) => first.x === last.x ? (left + right) / 2 : left + (x - first.x) / (last.x - first.x) * (right - left);
  const scaleY = (y: number) => bottom - (y - minY) / (maxY - minY) * (bottom - TOP);
  const tickCount = sameDay ? (width < 480 ? 2 : 4)
    : Math.min(width < 480 ? 2 : width < 800 ? 4 : 5, Math.max(2, Math.floor((last.x - first.x) / 86_400_000) + 1));
  const xTicks = first.x === last.x ? [first.x] : Array.from({ length: tickCount }, (_, index) => first.x + index / (tickCount - 1) * (last.x - first.x));
  const linePath = points.map((point, index) => `${index ? "L" : "M"} ${scaleX(point.x).toFixed(1)} ${scaleY(point.y).toFixed(1)}`).join(" ");
  const bandPoints = [...points.map((point) => `${scaleX(point.x)},${scaleY(point.high)}`),
    ...[...points].reverse().map((point) => `${scaleX(point.x)},${scaleY(point.low)}`)].join(" ");
  const selectIndex = (index: number) => setSelectedId(points[Math.max(0, Math.min(points.length - 1, index))].id);
  const selectPointer = (event: React.PointerEvent<SVGSVGElement>) => {
    const rect = event.currentTarget.getBoundingClientRect();
    const x = (event.clientX - rect.left) * width / rect.width;
    let nearest = 0;
    for (let index = 1; index < points.length; index++) {
      if (Math.abs(scaleX(points[index].x) - x) <= Math.abs(scaleX(points[nearest].x) - x)) nearest = index;
    }
    selectIndex(nearest);
  };

  return <section className="history-price-series trend-chart">
    <SeriesHeading item={items[0]} count={items.length} />
    <p className="trend-explanation">{join
      ? "The line follows the average price, or the range midpoint when no average is recorded. Shading shows the recorded price range."
      : complete ? "These records share the same time. A trend needs prices recorded at different times."
        : "Some measurement or type details were not recorded. Each price is shown separately; the points are not joined."}</p>
    <div className="trend-axis-captions"><span>Price (₦)</span><span>{sameDay ? "Time (WAT)" : "Date (WAT)"}</span></div>
    <div ref={plotRef} className="trend-plot" role="group" tabIndex={0}
      aria-label={`${items[0].commodity.name} price chart. Use the Left and Right arrow keys to inspect records.`}
      aria-describedby={`${chartId}-help`}
      onKeyDown={(event) => {
        if (!["ArrowLeft", "ArrowRight", "Home", "End"].includes(event.key)) return;
        event.preventDefault();
        selectIndex(event.key === "Home" ? 0 : event.key === "End" ? points.length - 1 : selectedIndex + (event.key === "ArrowLeft" ? -1 : 1));
      }}>
      <svg viewBox={`0 0 ${width} ${HEIGHT}`} role="img" aria-labelledby={`${chartId}-title ${chartId}-description`}
        onPointerMove={selectPointer} onPointerDown={selectPointer}>
        <title id={`${chartId}-title`}>{join ? "Price trend over time" : "Recorded prices over time"}</title>
        <desc id={`${chartId}-description`}>{items[0].commodity.name} at {items[0].market.name}. {points.length} records, from {shortPriceDate(first.date)} to {shortPriceDate(last.date)}. {join ? "Only matching recorded measurements and types are connected." : "Points are not connected and do not establish a comparable price trend."}</desc>
        {yTicks.map((value, index) => <g key={index}>
          <line className="trend-grid-line" x1={left} x2={right} y1={scaleY(value)} y2={scaleY(value)} />
          <text className="trend-y-tick" x={left - 10} y={scaleY(value) + 4} textAnchor="end">{currencyTick.format(value)}</text>
        </g>)}
        <line className="trend-axis" x1={left} x2={left} y1={TOP} y2={bottom} />
        <line className="trend-axis" x1={left} x2={right} y1={bottom} y2={bottom} />
        {xTicks.map((value, index) => <g key={index}>
          <line className="trend-axis" x1={scaleX(value)} x2={scaleX(value)} y1={bottom} y2={bottom + 5} />
          <text className="trend-x-tick" x={scaleX(value)} y={bottom + 24}
            textAnchor={xTicks.length === 1 ? "middle" : index === 0 ? "start" : index === xTicks.length - 1 ? "end" : "middle"}>{sameDay ? timeTick.format(value) : dateTick.format(value)}</text>
        </g>)}
        {join && <><polygon className="trend-band" points={bandPoints} /><path className="trend-line" d={linePath} fill="none" /></>}
        <line className="trend-cursor" x1={scaleX(selected.x)} x2={scaleX(selected.x)} y1={TOP} y2={bottom} />
        {points.map((point) => <g key={point.id}>
          <title>{shortPriceDate(point.date)}: {money(point.low)} – {money(point.high)}</title>
          <line className="trend-range" x1={scaleX(point.x)} x2={scaleX(point.x)} y1={scaleY(point.low)} y2={scaleY(point.high)} />
          <circle className={`trend-dot${point.id === selected.id ? " trend-dot-selected" : ""}`} cx={scaleX(point.x)} cy={scaleY(point.y)} r={point.id === selected.id ? 5 : 3} />
        </g>)}
      </svg>
    </div>
    <div className="trend-inspector">
      <output className="trend-selection" aria-live="polite" aria-atomic="true">
        <time dateTime={selected.date}>{shortPriceDate(selected.date)}</time>
        <strong>{money(selected.low)} – {money(selected.high)}</strong>
        <span>{selected.hasAverage ? "Recorded average" : "Range midpoint"}: {money(selected.y)}</span>
      </output>
      <div className="trend-controls">
        <button type="button" aria-label="Previous recorded price" onClick={() => selectIndex(selectedIndex - 1)} disabled={selectedIndex === 0}>←</button>
        <button type="button" aria-label="Next recorded price" onClick={() => selectIndex(selectedIndex + 1)} disabled={selectedIndex === points.length - 1}>→</button>
      </div>
    </div>
    <p className="trend-help" id={`${chartId}-help`}>Tap or hover over the chart, or use the arrows, to see each recorded price.</p>
  </section>;
}
