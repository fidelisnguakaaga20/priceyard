import { Link } from "react-router-dom";
import type { PriceUpdate } from "../types/api";
import { money, shortDate } from "../utils";

export function PriceCard({ item }: { item: PriceUpdate }) {
  return (
    <article className="card price-card">
      <div className="card-row">
        <div>
          <span className="eyebrow">{item.market.name}</span>
          <h3>{item.commodity.name}</h3>
        </div>
        <span className={`movement movement-${item.movement}`}>{item.movement}</span>
      </div>
      <p className="price-range">{money(item.price_low)} – {money(item.price_high)}</p>
      <p className="muted">{item.unit}{item.bag_size ? ` · ${item.bag_size}` : ""}</p>
      <div className="mini-grid">
        <span><strong>Confidence</strong>{item.confidence_level}</span>
        <span><strong>Updated</strong>{shortDate(item.update_date_time)}</span>
      </div>
      <Link className="text-link" to={`/commodities/${encodeURIComponent(item.commodity.name)}`}>View intelligence →</Link>
    </article>
  );
}
