import { relativePriceTime, priceAgingClass } from "../utils/priceTime";
import { useEffect, useMemo, useState } from "react";
import { useParams, useSearchParams } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { ConfidenceInfo } from "../components/ConfidenceInfo";
import { CostCalculator } from "../components/CostCalculator";
import { Disclaimer, MARKET_DISCLAIMER, PRICE_DISCLAIMER, STORAGE_DISCLAIMER } from "../components/Disclaimer";
import { FlagPriceButton } from "../components/FlagPriceButton";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { SavedPriceNotice } from "../components/SavedPriceNotice";
import { NativeShareButton } from "../components/ShareButtons";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch, apiFetchWithProvenance } from "../services/api";
import type { BuyingZone, CostBreakdown, Market, MarketSignal, PriceUpdate, QualitySignal, SellWatchWindow, StorageSuitability } from "../types/api";
import { commodityTitleColor, confidenceClass, isWithinSeasonalMonths, money, movementIcon, priceShareContent, shortDate, whatsAppShareUrl } from "../utils";
import "./commodity-detail.css";

export function CommodityDetailPage() {
  const { commodityName = "" } = useParams();
  const name = commodityName;
  const [searchParams] = useSearchParams();
  const requestedId = searchParams.get("commodity_id");
  const scope = requestedId !== null ? `id:${requestedId}` : `name:${name}`;
  const { token, user, hasFullAccess } = useAuth();
  const [priceResult, setPriceResult] = useState<{ name: string; items: PriceUpdate[]; savedAt: string | null }>({ name: "", items: [], savedAt: null });
  const prices = priceResult.name === scope ? priceResult.items : [];
  const displayName = prices[0]?.commodity.name || name;
  useDocumentTitle(displayName || "Commodity");
  const [signals, setSignals] = useState<MarketSignal[]>([]);
  const [quality, setQuality] = useState<QualitySignal[]>([]);
  const [zones, setZones] = useState<BuyingZone[]>([]);
  const [sellWatch, setSellWatch] = useState<SellWatchWindow[]>([]);
  const [storage, setStorage] = useState<StorageSuitability[]>([]);
  const [costs, setCosts] = useState<CostBreakdown[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [intelligenceError, setIntelligenceError] = useState("");
  const [loading, setLoading] = useState(true);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const marketMap = useMemo(() => new Map(markets.map((m) => [m.id, m.name])), [markets]);
  const marketLabel = (marketId: number) => marketMap.get(marketId) || `Market #${marketId}`;

  useEffect(() => {
    let current = true;
    setError("");
    setLoading(true);
    const query = new URLSearchParams();
    if (requestedId !== null) query.set("commodity_id", requestedId);
    else query.set("commodity", name);
    apiFetchWithProvenance<PriceUpdate[]>(`/price-updates?${query}`)
      .then(({ data, savedAt }) => {
        const items = requestedId !== null ? data : data.filter((item) => item.commodity.name.toLowerCase() === name.toLowerCase());
        // An old name-only bookmark cannot choose between legacy duplicate IDs.
        if (new Set(items.map((item) => item.commodity_id)).size > 1) throw new Error("Choose this commodity from Current Prices to view its records.");
        if (current) setPriceResult({ name: scope, items, savedAt });
      })
      .catch((err: Error) => { if (current) setError(err.message); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [scope]);

  useEffect(() => {
    let current = true;
    apiFetch<Market[]>("/markets").then((items) => { if (current) setMarkets(items); }).catch(() => undefined);
    return () => { current = false; };
  }, []);

  const commodityId = prices[0]?.commodity_id;

  useEffect(() => {
    let current = true;
    // Clear data belonging to an old commodity/account before another load.
    setSignals([]); setQuality([]); setZones([]); setSellWatch([]); setStorage([]); setCosts([]);
    setIntelligenceError("");
    if (!commodityId || !user || !hasFullAccess || !token) {
      setIntelligenceLoading(false);
      return;
    }
    setIntelligenceLoading(true);
    Promise.allSettled([
      apiFetch<MarketSignal[]>(`/market-signals?commodity_id=${commodityId}`, {}, token),
      apiFetch<QualitySignal[]>(`/quality-signals?commodity_id=${commodityId}`, {}, token),
      apiFetch<BuyingZone[]>(`/buying-zones?commodity_id=${commodityId}`, {}, token),
      apiFetch<SellWatchWindow[]>(`/sell-watch-windows?commodity_id=${commodityId}`, {}, token),
      apiFetch<StorageSuitability[]>(`/storage-suitability?commodity_id=${commodityId}`, {}, token),
      apiFetch<CostBreakdown[]>(`/cost-breakdowns?commodity_id=${commodityId}`, {}, token),
    ]).then((results) => {
      if (!current) return;
      const [marketSignals, qualitySignals, buyingZones, sellWindows, storageItems, costItems] = results;
      if (marketSignals.status === "fulfilled") setSignals(marketSignals.value.filter((item) => item.commodity_id === commodityId));
      if (qualitySignals.status === "fulfilled") setQuality(qualitySignals.value.filter((item) => item.commodity_id === commodityId));
      if (buyingZones.status === "fulfilled") setZones(buyingZones.value.filter((item) => item.commodity_id === commodityId));
      if (sellWindows.status === "fulfilled") setSellWatch(sellWindows.value.filter((item) => item.commodity_id === commodityId));
      if (storageItems.status === "fulfilled") setStorage(storageItems.value.filter((item) => item.commodity_id === commodityId));
      if (costItems.status === "fulfilled") setCosts(costItems.value.filter((item) => item.commodity_id === commodityId));
      const failure = results.find((result) => result.status === "rejected");
      if (failure?.status === "rejected") setIntelligenceError(failure.reason instanceof Error ? failure.reason.message : String(failure.reason));
    }).catch((err: Error) => { if (current) setIntelligenceError(err.message); })
      .finally(() => { if (current) setIntelligenceLoading(false); });
    return () => { current = false; };
  }, [commodityId, user?.id, hasFullAccess, token, name]);

  return <section className="page page-section commodity-detail-page">
    <div className="page-title detail-title-row commodity-page-intro">
      <CommodityImage src={prices[0]?.commodity.image_url} alt={displayName} className="commodity-image-detail" />
      <div className="commodity-intro-copy"><span className="eyebrow">Current market prices</span><h1 style={{ color: commodityTitleColor(displayName) }}>{displayName}</h1><p>Current prices by market and quantity.</p></div>
    </div>
    {(error || intelligenceError) && <div className="status-box error">{error || intelligenceError}</div>}
    {!loading && prices.length > 0 && <SavedPriceNotice savedAt={priceResult.savedAt} />}
    {loading ? <LoadingSpinner label={`Loading ${name} prices…`} /> : prices.length ? <div className="detail-grid">{prices.map((item) => <article key={item.id} className="card detail-card">
      <div className="card-row"><div><span className="eyebrow">{item.market.name}</span><h2>{money(item.price_low)} – {money(item.price_high)}</h2></div><span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span></div>
      <dl className="data-list"><div><dt>Previous range</dt><dd>{item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</dd></div><div><dt>Average</dt><dd>{money(item.average_price)}</dd></div><div><dt>Unit / bag</dt><dd>{item.unit}{item.bag_size ? ` / ${item.bag_size}` : ""}{item.commodity_type ? ` ? ${item.commodity_type}` : ""}</dd></div><div><dt>Market day / time</dt><dd>{item.market_day || item.market.market_day || "—"}{item.time_of_day ? ` · ${item.time_of_day}` : ""}</dd></div><div><dt>Status</dt><dd><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></dd></div><div><dt>Last updated</dt><dd className={priceAgingClass(item.update_date_time)}>{relativePriceTime(item.update_date_time)}</dd></div></dl>
      <div className="guidance"><div><span>Possible Meaning</span><p>{item.possible_meaning || "No observation supplied."}</p></div><div><span>Suggested Action</span><strong>{item.suggested_action || "Watch"}</strong><small>Observation, not guaranteed trading instruction.</small></div></div>
      {item.notes && <p className="price-card-note"><strong>Note from PriceYard:</strong> {item.notes}</p>}
      <div className="card-actions top-gap"><a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a><NativeShareButton content={priceShareContent(item)} /><FlagPriceButton priceUpdateId={item.id} /></div>
    </article>)}</div> : !error && <div className="status-box">No current approved {name} record is available.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>

    <div className="section-heading top-gap"><div><span className="eyebrow">Full-access intelligence</span><h2>Signals, quality, storage and decision support</h2></div></div>
    <PremiumGate>
      {intelligenceLoading ? <LoadingSpinner label="Loading full market intelligence…" /> : <div className="intelligence-grid">
        <article className="card"><h3>Market signals</h3>{signals.length ? signals.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.signal_type}</strong><p>{x.signal_description}</p>{x.possible_meaning && <small>{x.possible_meaning}</small>}</div>) : <p className="muted">No linked market signals currently available.</p>}<Disclaimer>{MARKET_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Quality readiness</h3>{quality.length ? quality.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.quality_status || "Quality observation"}</strong><p>Moisture: {x.moisture_status || "—"} · Storage readiness: {x.storage_readiness || "—"}</p>{x.risk_note && <small>{x.risk_note}</small>}</div>) : <p className="muted">No quality observation currently available.</p>}</article>
        <article className="card"><h3>Buying zone</h3>{zones.length ? zones.map((x) => { const today = new Date().toISOString().slice(0, 10); const outOfSeason = x.valid_from && x.valid_to && (today < x.valid_from || today > x.valid_to); return <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{money(x.price_low)} – {money(x.price_high)}</strong><p>{x.reason}</p><small>Confidence: {x.confidence}</small>{outOfSeason && <small className="season-note">Not currently in season — active {shortDate(x.valid_from)} to {shortDate(x.valid_to)}</small>}</div>; }) : <p className="muted">No buying-zone observation currently available.</p>}</article>
        <article className="card"><h3>Sell-watch window</h3>{sellWatch.length ? sellWatch.map((x) => { const inSeason = isWithinSeasonalMonths(x.start_period, x.end_period); return <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.start_period}{x.end_period ? ` – ${x.end_period}` : ""}</strong><p>{x.observation}</p><small>Confidence: {x.confidence}</small>{inSeason === false && <small className="season-note">Not currently in season</small>}</div>; }) : <p className="muted">No sell-watch observation currently available.</p>}</article>
        <article className="card"><h3>Storage suitability</h3>{storage.length ? storage.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.suitability_status.replace(/_/g, " ")}</strong><p>{x.summary || x.quality_storage_notes || "No summary supplied."}</p><small>Spoilage risk: {x.spoilage_risk || "—"} · Buyer availability: {x.buyer_availability || "—"}</small></div>) : <p className="muted">No storage-suitability observation currently available.</p>}<Disclaimer>{STORAGE_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Cost breakdown</h3>{costs.length ? costs.map((x) => {
          return <div className="stack-item" key={x.id}>
            <span className="eyebrow">{marketLabel(x.market_id)}</span>
            <CostCalculator breakdown={x} />
            <p className="cost-reference-label">Reference breakdown (Unit not recorded)</p>
            <p>Purchase reference: {money(x.purchase_price_reference)} · Additional costs: {money(x.total_additional_cost)}</p>
            <small>Transport {money(x.transport)} · Warehouse {money(x.warehouse)} · Market charges {money(x.market_charges)}</small>
          </div>;
        }) : <p className="muted">No cost breakdown currently linked to these current price records.</p>}</article>
      </div>}
    </PremiumGate>
  </section>;
}
