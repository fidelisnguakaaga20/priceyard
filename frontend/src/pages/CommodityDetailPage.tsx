import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { ConfidenceInfo } from "../components/ConfidenceInfo";
import { CostCalculator } from "../components/CostCalculator";
import { Disclaimer, MARKET_DISCLAIMER, PRICE_DISCLAIMER, STORAGE_DISCLAIMER } from "../components/Disclaimer";
import { FlagPriceButton } from "../components/FlagPriceButton";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { NativeShareButton } from "../components/ShareButtons";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { BuyingZone, Commodity, CostBreakdown, Market, MarketSignal, PriceUpdate, QualitySignal, SellWatchWindow, StorageSuitability } from "../types/api";
import { measurementLabel, outsideDateWindow } from "../lib/priceSeries.mjs";
import { agingClass, commodityTitleColor, confidenceClass, isWithinSeasonalMonths, money, movementIcon, priceShareContent, relativeTime, shortDate, whatsAppShareUrl } from "../utils";

export function CommodityDetailPage() {
  const { commodityName = "" } = useParams();
  const name = commodityName;
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
  const [commodity, setCommodity] = useState<Commodity | null>(null);
  const [metadataError, setMetadataError] = useState("");
  const [selectedMarket, setSelectedMarket] = useState("");
  const [sectionErrors, setSectionErrors] = useState<Record<string, string>>({});
  const [sectionBusy, setSectionBusy] = useState<Record<string, boolean>>({});
  const [retry, setRetry] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const marketMap = useMemo(() => new Map(markets.map((m) => [m.id, m.name])), [markets]);
  const marketLabel = (marketId: number) => marketMap.get(marketId) || `Market #${marketId}`;

  useEffect(() => {
    const controller = new AbortController();
    setCommodity(null);
    setPrices([]);
    setMetadataError("");
    setLoading(true);
    void apiFetch<Commodity[]>("/commodities", { signal: controller.signal }).then((items) => {
      if (controller.signal.aborted) return;
      const matching = items.filter((item) => item.name.trim().toLowerCase() === name.trim().toLowerCase());
      if (matching.length !== 1) { setMetadataError("This commodity is unavailable or cannot be identified safely."); setLoading(false); return; }
      setCommodity(matching[0]);
    }).catch((err: Error) => { if (!controller.signal.aborted) { setMetadataError(err.message); setLoading(false); } });
    void apiFetch<Market[]>("/markets", { signal: controller.signal }).then((items) => { if (!controller.signal.aborted) setMarkets(items); }).catch(() => undefined);
    return () => controller.abort();
  }, [name, retry]);

  const commodityId = commodity?.id;

  useEffect(() => {
    if (!commodityId) return;
    const controller = new AbortController();
    setError("");
    setLoading(true);
    setPrices([]);
    const query = new URLSearchParams({ commodity_id: String(commodityId) });
    if (selectedMarket) query.set("market_id", selectedMarket);
    void apiFetch<PriceUpdate[]>(`/price-updates?${query}`, { signal: controller.signal }, token)
      .then((items) => { if (!controller.signal.aborted) setPrices(items); })
      .catch((err: Error) => { if (!controller.signal.aborted) setError(err.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [commodityId, selectedMarket, token, retry]);

  useEffect(() => {
    if (!commodityId || !user || !hasFullAccess || !token) {
      setSignals([]); setQuality([]); setZones([]); setSellWatch([]); setStorage([]); setCosts([]);
      setSectionErrors({});
      setIntelligenceLoading(false);
      return;
    }
    const controller = new AbortController();
    setSignals([]); setQuality([]); setZones([]); setSellWatch([]); setStorage([]); setCosts([]);
    setSectionErrors({});
    setIntelligenceLoading(true);
    const query = new URLSearchParams({ commodity_id: String(commodityId) });
    if (selectedMarket) query.set("market_id", selectedMarket);
    function section<T extends { commodity_id: number }>(key: string, path: string, assign: (items: T[]) => void) {
      setSectionBusy((state) => ({ ...state, [key]: true }));
      return apiFetch<T[]>(`${path}?${query}`, { signal: controller.signal }, token)
        .then((items) => { if (!controller.signal.aborted) assign(items.filter((item) => item.commodity_id === commodityId)); })
        .catch((err: Error) => { if (!controller.signal.aborted) setSectionErrors((state) => ({ ...state, [key]: err.message })); })
        .finally(() => { if (!controller.signal.aborted) setSectionBusy((state) => ({ ...state, [key]: false })); });
    }
    void Promise.allSettled([
      section<MarketSignal>("signals", "/market-signals", setSignals), section<QualitySignal>("quality", "/quality-signals", setQuality),
      section<BuyingZone>("zones", "/buying-zones", setZones), section<SellWatchWindow>("sell", "/sell-watch-windows", setSellWatch),
      section<StorageSuitability>("storage", "/storage-suitability", setStorage), section<CostBreakdown>("costs", "/cost-breakdowns", setCosts),
    ]).finally(() => { if (!controller.signal.aborted) setIntelligenceLoading(false); });
    return () => controller.abort();
  }, [commodityId, selectedMarket, user, hasFullAccess, token, retry]);

  const sectionState = (key: string, empty: string) => sectionErrors[key]
    ? <div className="status-box error">Could not load this section: {sectionErrors[key]}<button className="button button-small" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>
    : <p className="muted">{sectionBusy[key] ? "Loading this section…" : empty}</p>;

  return <section className="page page-section">
    <div className="page-title detail-title-row">
      <CommodityImage src={commodity?.image_url} alt={name} className="commodity-image-detail" />
      <div><span className="eyebrow">Commodity intelligence</span><h1 style={{ color: commodityTitleColor(name) }}>{name}</h1><p>Current approved market records plus full-access intelligence where your subscription permits.</p></div>
    </div>
    {metadataError && <div className="status-box error">{metadataError}<button className="button button-small" onClick={() => setRetry((value) => value + 1)}>Retry</button></div>}
    <label>Market<select value={selectedMarket} onChange={(event) => setSelectedMarket(event.target.value)}><option value="">All markets</option>{markets.map((item) => <option value={item.id} key={item.id}>{item.name}{item.state ? ` (${item.state})` : ""}</option>)}</select></label>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <LoadingSpinner label={`Loading ${name} prices…`} /> : prices.length ? <div className="detail-grid">{prices.map((item) => <article key={item.id} className="card detail-card">
      <div className="card-row"><div><span className="eyebrow">{item.market.name}</span><h2>{money(item.price_low)} – {money(item.price_high)}</h2></div><span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span></div>
      <dl className="data-list"><div><dt>Previous range</dt><dd>{item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</dd></div><div><dt>Average</dt><dd>{money(item.average_price)}</dd></div><div><dt>Unit / bag</dt><dd>{measurementLabel(item)}</dd></div><div><dt>Market day / time</dt><dd>{item.market_day || item.market.market_day || "—"}{item.time_of_day ? ` · ${item.time_of_day}` : ""}</dd></div><div><dt>Status</dt><dd><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span><ConfidenceInfo /></dd></div><div><dt>Last updated</dt><dd className={agingClass(item.update_date_time)}>{relativeTime(item.update_date_time)}</dd></div></dl>
      {(item.possible_meaning || item.suggested_action) && <div className="guidance"><div><span>Possible Meaning</span><p>{item.possible_meaning || "No observation supplied."}</p></div><div><span>Suggested Action</span><strong>{item.suggested_action || "Watch"}</strong><small>Observation, not guaranteed trading instruction.</small></div></div>}
      {item.notes && <p className="price-card-note"><strong>Note from PriceYard:</strong> {item.notes}</p>}
      <div className="card-actions top-gap"><a className="text-link" href={whatsAppShareUrl(item)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a><NativeShareButton content={priceShareContent(item)} /><FlagPriceButton priceUpdateId={item.id} /></div>
    </article>)}</div> : !error && <div className="status-box">No current approved {name} record is available.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>

    <div className="section-heading top-gap"><div><span className="eyebrow">Full-access intelligence</span><h2>Signals, quality, storage and decision support</h2></div></div>
    <PremiumGate>
      <>{intelligenceLoading && <LoadingSpinner label="Loading market intelligence…" />}<div className="intelligence-grid">
        <article className="card"><h3>Market signals</h3>{signals.length ? signals.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.signal_type}</strong><p>{x.signal_description}</p>{x.possible_meaning && <small>{x.possible_meaning}</small>}</div>) : sectionState("signals", "No linked market signals currently available.")}<Disclaimer>{MARKET_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Quality readiness</h3>{quality.length ? quality.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.quality_status || "Quality observation"}</strong><p>Moisture: {x.moisture_status || "—"} · Storage readiness: {x.storage_readiness || "—"}</p>{x.risk_note && <small>{x.risk_note}</small>}</div>) : sectionState("quality", "No quality observation currently available.")}</article>
        <article className="card"><h3>Buying zone</h3>{zones.length ? zones.map((x) => { const outOfSeason = outsideDateWindow(x.valid_from, x.valid_to); return <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{money(x.price_low)} – {money(x.price_high)}</strong><p>{x.reason}</p><small>Confidence: {x.confidence}</small>{outOfSeason && <small className="season-note">Not currently in season — active {shortDate(x.valid_from)} to {shortDate(x.valid_to)}</small>}</div>; }) : sectionState("zones", "No buying-zone observation currently available.")}</article>
        <article className="card"><h3>Sell-watch window</h3>{sellWatch.length ? sellWatch.map((x) => { const inSeason = isWithinSeasonalMonths(x.start_period, x.end_period); return <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.start_period}{x.end_period ? ` – ${x.end_period}` : ""}</strong><p>{x.observation}</p><small>Confidence: {x.confidence}</small>{inSeason === false && <small className="season-note">Not currently in season</small>}</div>; }) : sectionState("sell", "No sell-watch observation currently available.")}</article>
        <article className="card"><h3>Storage suitability</h3>{storage.length ? storage.map((x) => <div className="stack-item" key={x.id}><span className="eyebrow">{marketLabel(x.market_id)}</span><strong>{x.suitability_status.replace(/_/g, " ")}</strong><p>{x.summary || x.quality_storage_notes || "No summary supplied."}</p><small>Spoilage risk: {x.spoilage_risk || "—"} · Buyer availability: {x.buyer_availability || "—"}</small></div>) : sectionState("storage", "No storage-suitability observation currently available.")}<Disclaimer>{STORAGE_DISCLAIMER}</Disclaimer></article>
        <article className="card"><h3>Cost breakdown</h3>{costs.length ? costs.map((x) => {
          const unitLabel = measurementLabel({ unit: x.unit || "", bag_size: x.bag_size || null, commodity_type: x.commodity_type || null, grade: x.grade || null });
          return <div className="stack-item" key={x.id}>
            <span className="eyebrow">{marketLabel(x.market_id)}</span>
            {x.unit && x.bag_size ? <CostCalculator breakdown={x} unitLabel={unitLabel} /> : <p className="status-box">The measurement was not recorded. These historical amounts are shown as supplied; a quantity calculation is unavailable.</p>}
            {x.reference_date_time && <small>Reference observation: {shortDate(x.reference_date_time)}</small>}
            <p className="cost-reference-label">Reference breakdown (per {unitLabel})</p>
            <p>Purchase reference: {money(x.purchase_price_reference)} · Additional costs: {money(x.total_additional_cost)}</p>
            <small>Transport {money(x.transport)} · Warehouse {money(x.warehouse)} · Market charges {money(x.market_charges)}</small>
          </div>;
        }) : sectionState("costs", "No cost breakdown currently available for this commodity.")}</article>
      </div></>
    </PremiumGate>
  </section>;
}
