import { useState } from "react";
import { Link } from "react-router-dom";
import { CommodityImage } from "./CommodityImage";
import { ConfidenceInfo } from "./ConfidenceInfo";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch, ApiError } from "../services/api";
import type { PriceUpdate } from "../types/api";
import { confidenceClass, money, movementIcon, relativeTime, whatsAppShareUrl } from "../utils";

export function PriceCard({ item }: { item: PriceUpdate }) {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [saving, setSaving] = useState(false);
  const [watched, setWatched] = useState(false);

  const watchThis = async () => {
    if (!token || saving || watched) return;
    setSaving(true);
    try {
      await apiFetch("/watchlist", {
        method: "POST",
        body: JSON.stringify({ commodity_id: item.commodity_id, market_id: item.market_id }),
      }, token);
      setWatched(true);
      showToast("Added to your watchlist.");
    } catch (err) {
      if (err instanceof ApiError && err.status === 409) {
        setWatched(true);
        showToast("Already on your watchlist.");
      } else {
        showToast((err as Error).message, "error");
      }
    } finally {
      setSaving(false);
    }
  };

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
        <span><strong>Status</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></span>
        <span><strong>Updated</strong>{relativeTime(item.update_date_time)}</span>
      </div>
      <div className="card-actions">
        <Link className="text-link-cta" to={`/commodities/${encodeURIComponent(item.commodity.name)}`}>See what this price means →</Link>
        <a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
        {token ? (
          <button type="button" className="text-link text-link-button" onClick={() => void watchThis()} disabled={saving || watched}>
            {watched ? "★ Watching" : saving ? "Saving…" : "★ Watch this"}
          </button>
        ) : (
          <Link className="text-link" to="/login">Log in to watch this →</Link>
        )}
      </div>
    </article>
  );
}
