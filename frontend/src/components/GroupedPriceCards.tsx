import { CommodityImage } from "./CommodityImage";
import { PriceCard } from "./PriceCard";
import type { PriceUpdate } from "../types/api";
import { commodityTitleColor } from "../utils";

/** Share the commodity photo, without combining or dropping its recorded prices. */
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
      return <article className="card price-card commodity-price-card" key={commodityId} aria-labelledby={headingId}>
        <CommodityImage src={commodity.image_url} alt={commodity.name} />
        <h2 id={headingId} style={{ color: commodityTitleColor(commodity.name) }}>{commodity.name}</h2>
        <div className="price-options">
          {prices.map((item) => <PriceCard key={item.id} item={item} compact />)}
        </div>
      </article>;
    })}
  </div>;
}
