import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { ConfidenceInfo } from "../components/ConfidenceInfo";
import { Disclaimer, MARKET_DISCLAIMER, PRICE_DISCLAIMER, STORAGE_DISCLAIMER } from "../components/Disclaimer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { BuyingZone, CostBreakdown, Market, MarketSignal, PriceUpdate, QualitySignal, SellWatchWindow, StorageSuitability } from "../types/api";
import { commodityTitleColor, confidenceClass, money, movementIcon, relativeTime, whatsAppShareUrl } from "../utils";

export function CommodityDetailPage() {
  const { commodityName = "" } = useParams();
  const name = decodeURIComponent(commodityName);
  useDocumentTitle(name || "Commodity");
  const { token, user, hasFullAccess } = useAuth();
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [signals, setSignals] = useState<MarketSignal[]>([]);
  const [quality, setQuality] = useState<QualitySignal[]>([]);
  const [zones, setZones] = useState<BuyingZone[]>([]);
  const [sellWatch, setSellWatch] = useState<SellWatchWindow[]>([]);
  const [storage, setStorage] = useState<StorageSuitability[]>([]);
  const [costs, setCosts] = useState<CostBreakdown[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const marketMap = useMemo(() => new Map(markets.map((m) => [m.id, m.name])), [markets]);
  const marketLabel = (marketId: number) => marketMap.get(marketId) || `Market #${marketId}`;

  useEffect(() => {
    setError("");
    setLoading(true);
    apiFetch<PriceUpdate[]>(`/price-updates?commodity=${encodeURIComponent(name)}`)
      .then(setPrices)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, [name]);

  useEffect(() => {
    apiFetch<Market[]>("/markets").then(setMarkets).catch(() => undefined);
  }, []);

  const commodityId = prices[0]?.commodity_id;
  const priceIds = useMemo(() => new Set(prices.map((p) => p.id)), [prices]);

  useEffect(() => {
    if (!commodityId || !user || !hasFullAccess || !token) {
      setIntelligenceLoading(false);
      return;
    }
    setIntelligenceLoading(true);
    Promise.all([
      apiFetch<MarketSignal[]>("/market-signals", {}, token),
      apiFetch<QualitySignal[]>("/quality-signals", {}, token),
      apiFetch<BuyingZone[]>("/buying-zones", {}, token),
      apiFetch<SellWatchWindow[]>("/sell-watch-windows", {}, token),
      apiFetch<StorageSuitability[]>("/storage-suitability", {}, token),
      apiFetch<CostBreakdown[]>("/cost-breakdowns", {}, token),
    ]).then(([marketSignals, qualitySignals, buyingZones, sellWindows, storageItems, costItems]) => {
      setSignals(marketSignals.filter((item) => item.commodity_id === commodityId));
      setQuality(qualitySignals.filter((item) => item.commodity_id === commodityId));
      setZones(buyingZones.filter((item) => item.commodity_id === commodityId));
      setSellWatch(sellWindows.filter((item) => item.commodity_id === commodityId));
      setStorage(storageItems.filter((item) => item.commodity_id === commodityId));
      setCosts(costItems.filter((item) => priceIds.has(item.price_update_id)));
    }).catch(() => undefined).finally(() => setIntelligenceLoading(false));
  }, [commodityId, user, hasFullAccess, token, priceIds]);

  return <section className="page page-section">
    <div className="page-title detail-title-row">
      <CommodityImage src={prices[0]?.commodity.image_url} alt={name} className="commodity-image-detail" />
      <div><span className="eyebrow">Commodity intelligence</span><h1 style={{ color: commodityTitleColor(name) }}>{name}</h1><p>Current approved market records plus full-access intelligence where your subscription permits.</p></div>
    </div>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <LoadingSpinner label={`Loading ${name} prices…`} /> : prices.length ? <div className="detail-grid">{prices.map((item) => <article key={item.id} className="card detail-card">
      <div className="card-row"><div><span className="eyebrow">{item.market.name}</span><h2>{money(item.price_low)} – {money(item.price_high)}</h2></div><span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span></div>
      <dl className="data-list"><div><dt>Previous range</dt><dd>{item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</dd></div><div><dt>Average</dt><dd>{money(item.average_price)}</dd></div><div><dt>Unit / bag</dt><dd>{item.unit}{item.bag_size ? ` / ${item.bag_size}` : ""}</dd></div><div><dt>Market day / time</dt><dd>{item.market_day || item.market.market_day || "—"}{item.time_of_day ? ` · ${item.time_of_day}` : ""}</dd></div><div><dt>Status</dt><dd><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></dd></div><div><dt>Last updated</dt><dd>{relativeTime(item.update_date_time)}</dd></div></dl>
      <div className="guidance"><div><span>Possible Meaning</span><p>{item.possible_meaning || "No observation supplied."}</p></div><div><span>Suggested Action</span><strong>{item.suggested_action || "Watch"}</strong><small>Observation, not guaranteed trading instruction.</small></div></div>
      {item.notes && <p className="price-card-note"><strong>Note from PriceYard:</strong> {item.notes}</p>}
      <div className="card-actions top-gap"><a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a></div>
    </article>)}</div> : !error && <div className="status-box">No current approved {name} record is available.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>

    <div className="section-heading top-gap"><div><span className="eyebrow">Full-access intelligence</span><h2>Signals, quality, storage and decision support</h2></div></div>
    <PremiumGate>
      {intelligenceLoading ? <LoadingSpinner label="Loading full market intelligence…" /> : <div className="intelligence-grid">
        <article className="card"><h3>Market signals</h3>{signals.length ? signals.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.signal_type}</strong><p>{x.signal_description}</p>{x.possible_meaning && <small>{x.possible_meaning}</small>}</div>) : <p className="muted">No linked market signals currently available.</p>}<Disclaimer>{MARKET_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Quality readiness</h3>{quality.length ? quality.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.quality_status || "Quality observation"}</strong><p>Moisture: {x.moisture_status || "—"} · Storage readiness: {x.storage_readiness || "—"}</p>{x.risk_note && <small>{x.risk_note}</small>}</div>) : <p className="muted">No quality observation currently available.</p>}</article>
        <article className="card"><h3>Buying zone</h3>{zones.length ? zones.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{money(x.price_low)} – {money(x.price_high)}</strong><p>{x.reason}</p><small>Confidence: {x.confidence}</small></div>) : <p className="muted">No buying-zone observation currently available.</p>}</article>
        <article className="card"><h3>Sell-watch window</h3>{sellWatch.length ? sellWatch.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.start_period}{x.end_period ? ` – ${x.end_period}` : ""}</strong><p>{x.observation}</p><small>Confidence: {x.confidence}</small></div>) : <p className="muted">No sell-watch observation currently available.</p>}</article>
        <article className="card"><h3>Storage suitability</h3>{storage.length ? storage.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.suitability_status.replace(/_/g, " ")}</strong><p>{x.summary || x.quality_storage_notes || "No summary supplied."}</p><small>Spoilage risk: {x.spoilage_risk || "—"} · Buyer availability: {x.buyer_availability || "—"}</small></div>) : <p className="muted">No storage-suitability observation currently available.</p>}<Disclaimer>{STORAGE_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Cost breakdown</h3>{costs.length ? costs.map((x) => <div className="stack-item" key={x.id}><strong>Estimated landing/storage: {money(x.total_estimated_landing_storage_cost)}</strong><p>Purchase reference: {money(x.purchase_price_reference)} · Additional costs: {money(x.total_additional_cost)}</p><small>Transport {money(x.transport)} · Warehouse {money(x.warehouse)} · Market charges {money(x.market_charges)}</small></div>) : <p className="muted">No cost breakdown currently linked to these current price records.</p>}</article>
      </div>}
    </PremiumGate>
  </section>;
}
