import { useEffect, useState } from "react";
import { CommodityImage } from "./CommodityImage";
import { PriceCard } from "./PriceCard";
import type { PriceUpdate } from "../types/api";
import { commodityTitleColor } from "../utils";
import { priceEpoch, shortPriceDate } from "../utils/priceTime";
import "./grouped-price-cards.css";

function newestFirst(left: PriceUpdate, right: PriceUpdate): number {
  const leftTime = priceEpoch(left.update_date_time);
  const rightTime = priceEpoch(right.update_date_time);
  const leftValid = Number.isFinite(leftTime);
  const rightValid = Number.isFinite(rightTime);
  if (leftValid && rightValid && leftTime !== rightTime) return rightTime - leftTime;
  if (leftValid !== rightValid) return leftValid ? -1 : 1;
  return right.id - left.id;
}

function MarketPriceSummary({ prices }: { prices: PriceUpdate[] }) {
  // Only an explicit user choice persists. Otherwise new approved records can
  // become the default during the existing background refresh.
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const options = [...prices].sort(newestFirst);
  const selected = options.find((item) => item.id === selectedId) ?? options[0];

  useEffect(() => {
    if (selectedId !== null && !prices.some((item) => item.id === selectedId)) setSelectedId(null);
  }, [prices, selectedId]);

  return <div className="market-price-summary">
    {options.length > 1 && <label className="price-option-selection">
      <span>Size / grade <small>({options.length} recorded options)</small></span>
      <select className="price-option-select" value={selected.id}
        aria-label={`Size / grade at ${selected.market.name} for ${selected.commodity.name}`}
        onChange={(event) => setSelectedId(Number(event.target.value))}>
        {options.map((item, index) => <option key={item.id} value={item.id}>
          {[item.unit, item.bag_size, item.commodity_type].filter(Boolean).join(" · ")}
          {` — ${shortPriceDate(item.update_date_time)}${index === 0 ? " (latest)" : ""}`}
        </option>)}
      </select>
    </label>}
    <PriceCard key={selected.id} item={selected} compact />
  </div>;
}

/** One current summary per market; recorded sizes/types remain selectable. */
export function GroupedPriceCards({ items }: { items: PriceUpdate[] }) {
  const groups = new Map<number, PriceUpdate[]>();
  for (const item of items) {
    const group = groups.get(item.commodity_id) ?? [];
    group.push(item);
    groups.set(item.commodity_id, group);
  }

  return <div className="card-grid">
    {[...groups.entries()].map(([commodityId, prices]) => {
      const commodity = prices[0].commodity;
      const headingId = `commodity-prices-${commodityId}`;
      const markets = new Map<number, PriceUpdate[]>();
      for (const item of prices) {
        const options = markets.get(item.market_id) ?? [];
        options.push(item);
        markets.set(item.market_id, options);
      }
      return <article className="card price-card commodity-price-card" key={commodityId} aria-labelledby={headingId}>
        <CommodityImage src={commodity.image_url} alt={commodity.name} />
        <h2 id={headingId} style={{ color: commodityTitleColor(commodity.name) }}>{commodity.name}</h2>
        <div className="price-options">
          {[...markets.entries()].map(([marketId, options]) => <MarketPriceSummary key={marketId} prices={options} />)}
        </div>
      </article>;
    })}
  </div>;
}
