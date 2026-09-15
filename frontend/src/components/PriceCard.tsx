import { Link } from "react-router-dom";
import { CommodityImage } from "./CommodityImage";
import { ConfidenceInfo } from "./ConfidenceInfo";
import type { PriceUpdate } from "../types/api";
import { confidenceClass, money, movementIcon, relativeTime, whatsAppShareUrl } from "../utils";

export function PriceCard({ item }: { item: PriceUpdate }) {
  return (
    <article className="card price-card">
      <CommodityImage src={item.commodity.image_url} alt={item.commodity.name} />
      <div className="card-row">
        <div>
          <span className="eyebrow">{item.market.name}</span>
          <h3>{item.commodity.name}</h3>
        </div>
        <span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span>
      </div>
      <p className="price-range">{money(item.price_low)} – {money(item.price_high)}</p>
      <p className="muted">{item.unit}{item.bag_size ? ` · ${item.bag_size}` : ""}</p>
      <div className="mini-grid">
        <span><strong>Confidence</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></span>
        <span><strong>Updated</strong>{relativeTime(item.update_date_time)}</span>
      </div>
      <div className="card-actions">
        <Link className="text-link" to={`/commodities/${encodeURIComponent(item.commodity.name)}`}>See full price details →</Link>
        <a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
      </div>
    </article>
  );
}
