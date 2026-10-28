import { relativePriceTime, priceAgingClass, priceEpoch, shortPriceDate } from "../utils/priceTime";
import { useState } from "react";
import { Link } from "react-router-dom";
import { CommodityImage } from "./CommodityImage";
import { ConfidenceInfo } from "./ConfidenceInfo";
import { FlagPriceButton } from "./FlagPriceButton";
import { NativeShareButton } from "./ShareButtons";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch, ApiError } from "../services/api";
import { commodityLink, priceHistoryLink } from "../services/priceIdentity";
import type { PriceUpdate } from "../types/api";
import { commodityTitleColor, confidenceClass, money, movementIcon, priceShareContent, whatsAppShareUrl } from "../utils";
import "./market-update-note.css";

export function PriceCard({ item, compact = false }: { item: PriceUpdate; compact?: boolean }) {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [saving, setSaving] = useState(false);
  const [watched, setWatched] = useState(false);
  // Only an explicitly published public note becomes a market update. Keep
  // Possible Meaning and all other guidance out of this notice.
  const marketUpdate = item.notes?.trim().replace(/^Market update:\s*/i, "").trim();
  const hasMarketUpdate = !!marketUpdate && /^Market update:\s*/i.test(item.notes?.trim() || "");

  const watchThis = async () => {
    if (!token || saving || watched) return;
    setSaving(true);
    try {
      await apiFetch("/watchlist", {
        method: "POST",
        body: JSON.stringify({ commodity_id: item.commodity_id, market_id: item.market_id }),
      }, token);
      setWatched(true);
      showToast("Added to your watchlist — we'll email you when this price changes.", "success", { label: "Invite a friend for extra trial days →", to: "/dashboard" });
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

  const Container = compact ? "section" : "article";
  return (
    <Container className={compact ? "price-card price-option" : "card price-card"}>
      {!compact && <CommodityImage src={item.commodity.image_url} alt={item.commodity.name} />}
      <div className="card-row">
        <div>
          {compact ? <h3>{item.market.name}</h3> : <>
            <span className="eyebrow">{item.market.name}</span>
            <h3 style={{ color: commodityTitleColor(item.commodity.name) }}>{item.commodity.name}</h3>
          </>}
        </div>
        <span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span>
      </div>
      {hasMarketUpdate && <aside className="market-update-note" aria-label="Market update">
        <p><strong>Market update:</strong> {marketUpdate}</p>
        <div className="market-update-date">Price report: {Number.isFinite(priceEpoch(item.update_date_time))
          ? <time dateTime={item.update_date_time}>{shortPriceDate(item.update_date_time)}</time>
          : "Date not confirmed"}</div>
      </aside>}
      <p className="price-range">{money(item.price_low)} – {money(item.price_high)}</p>
      <p className="muted">{item.unit}{item.bag_size ? ` · ${item.bag_size}` : ""}{item.commodity_type ? ` · ${item.commodity_type}` : ""}</p>
      <div className="mini-grid">
        <span><strong>Status</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></span>
        <span><strong>Updated</strong><span className={priceAgingClass(item.update_date_time)}>{relativePriceTime(item.update_date_time)}</span></span>
      </div>
      {item.notes && !hasMarketUpdate && <p className="price-card-note"><strong>Note from PriceYard:</strong> {item.notes}</p>}
      <div className="card-actions">
        <Link className="text-link-cta" to={commodityLink(item.commodity)}>See what this price means →</Link>
        <Link className="text-link" to={priceHistoryLink(item)}>View price history</Link>
        <a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
        <NativeShareButton content={priceShareContent(item)} />
        {token ? (
          <button type="button" className={watched ? "button button-secondary button-small" : "button button-small"} onClick={() => void watchThis()} disabled={saving || watched}>
            {watched ? "★ Watching" : saving ? "Saving…" : "★ Watch this"}
          </button>
        ) : (
          <Link className="button button-ghost button-small" to="/login">Log in to watch this →</Link>
        )}
        <FlagPriceButton priceUpdateId={item.id} />
      </div>
    </Container>
  );
}
