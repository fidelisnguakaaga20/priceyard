import { useEffect, useMemo, useState } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { CostCalculator } from "../components/CostCalculator";
import { Disclaimer, MARKET_DISCLAIMER, STORAGE_DISCLAIMER } from "../components/Disclaimer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { BuyingZone, Commodity, CostBreakdown, Market, MarketSignal, QualitySignal, SellWatchWindow, StorageSuitability } from "../types/api";
import { commodityTitleColor, humanize, money, shortDate } from "../utils";
import "./commodity-detail.css";

export function CommodityDetailPage() {
  const { commodityName = "" } = useParams();
  const name = commodityName;
  const [searchParams] = useSearchParams();
  const requestedId = searchParams.get("commodity_id");
  const scope = requestedId !== null ? `id:${requestedId}` : `name:${name}`;
  const { token, user, hasFullAccess } = useAuth();
  const [commodityResult, setCommodityResult] = useState<{ scope: string; item: Commodity | null }>({ scope: "", item: null });
  const commodity = commodityResult.scope === scope ? commodityResult.item : null;
  const displayName = commodity?.name || name;
  useDocumentTitle(displayName ? `${displayName} market insights` : "Market insights");
  const [signals, setSignals] = useState<MarketSignal[]>([]);
  const [quality, setQuality] = useState<QualitySignal[]>([]);
  const [zones, setZones] = useState<BuyingZone[]>([]);
  const [sellWatch, setSellWatch] = useState<SellWatchWindow[]>([]);
  const [storage, setStorage] = useState<StorageSuitability[]>([]);
  const [costs, setCosts] = useState<CostBreakdown[]>([]);
  // Tracks which insight sections failed to load (vs. genuinely have nothing
  // entered) so the two cases never show the same "No X available" message.
  const [failedSections, setFailedSections] = useState<Set<string>>(new Set());
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [intelligenceError, setIntelligenceError] = useState("");
  const [loading, setLoading] = useState(true);
  const [intelligenceLoading, setIntelligenceLoading] = useState(false);
  const [intelligenceContext, setIntelligenceContext] = useState<{ scope: string; userId: number; token: string } | null>(null);
  const intelligenceReady = intelligenceContext?.scope === scope && intelligenceContext?.userId === user?.id && intelligenceContext?.token === token;
  const marketMap = useMemo(() => new Map(markets.map((m) => [m.id, m.name])), [markets]);
  // Admin-only shortcut straight to the record's existing Admin form, pre-selected
  // by id, instead of leaving an admin to hunt for it by hand.
  const editLink = (adminPath: string, id: number) => user?.role === "admin"
    ? <Link className="text-link insight-edit-link" to={`/admin/${adminPath}?id=${id}`}>Edit</Link> : null;
  const marketLabel = (marketId: number) => marketMap.get(marketId) || `Market #${marketId}`;

  useEffect(() => {
    let current = true;
    setError("");
    setLoading(true);
    const loadCommodity = async () => {
      if (requestedId !== null) return apiFetch<Commodity>(`/commodities/${encodeURIComponent(requestedId)}`);
      const items = (await apiFetch<Commodity[]>("/commodities"))
        .filter((item) => item.name.toLowerCase() === name.toLowerCase());
      // An old name-only bookmark cannot choose between legacy duplicate IDs.
      if (items.length > 1) throw new Error("Choose this commodity from Current Prices to view its market insights.");
      return items[0] || null;
    };
    loadCommodity().then((item) => { if (current) setCommodityResult({ scope, item }); })
      .catch((err: Error) => { if (current) setError(err.message); })
      .finally(() => { if (current) setLoading(false); });
    return () => { current = false; };
  }, [scope]);

  useEffect(() => {
    let current = true;
    apiFetch<Market[]>("/markets").then((items) => { if (current) setMarkets(items); }).catch(() => undefined);
    return () => { current = false; };
  }, []);

  const commodityId = commodity?.id;

  useEffect(() => {
    let current = true;
    // Clear data belonging to an old commodity/account before another load.
    setSignals([]); setQuality([]); setZones([]); setSellWatch([]); setStorage([]); setCosts([]);
    setFailedSections(new Set());
    setIntelligenceContext(null);
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
      const sectionNames = ["signals", "quality", "zones", "sellWatch", "storage", "costs"] as const;
      setFailedSections(new Set(sectionNames.filter((_, i) => results[i].status === "rejected")));
      // One section failing (often a cold-start blip) shouldn't block the others --
      // each already shows its own "no data" state. Only surface a banner, in plain
      // language rather than the raw fetch error, if every section failed together.
      if (results.every((result) => result.status === "rejected")) {
        setIntelligenceError("Market insights could not load right now. Please refresh the page.");
      }
    }).catch((err: Error) => { if (current) setIntelligenceError(err.message); })
      .finally(() => { if (current) {
        setIntelligenceLoading(false);
        setIntelligenceContext({ scope, userId: user.id, token });
      } });
    return () => { current = false; };
  }, [commodityId, user?.id, hasFullAccess, token, name, scope]);

  return <section className="page page-section commodity-detail-page">
    <div className="page-title detail-title-row commodity-page-intro">
      <CommodityImage src={commodity?.image_url} alt={displayName} className="commodity-image-detail" />
      <div className="commodity-intro-copy"><span className="eyebrow">Full-access insights</span><h1 style={{ color: commodityTitleColor(displayName) }}>{displayName}</h1><p>Understand price changes, quality and storage.</p></div>
    </div>
    {(error || intelligenceError) && <div className="status-box error">{error || intelligenceError}</div>}
    {loading ? <LoadingSpinner label={`Loading ${name} market insights…`} /> : commodity ? <>
    <div className="section-heading"><h2>Market insights</h2></div>
    <PremiumGate description={user ? "Full access needed to see this commodity’s market insights. Check your trial or subscription below." : "Sign in or register free to see this commodity’s market insights."}>
      {intelligenceLoading || !intelligenceReady ? <LoadingSpinner label="Loading full market insights…" /> : <div className="intelligence-grid market-insights-grid">
        <article className="card insight-card insight-card-signals"><h3>📊 Market signals</h3>{signals.length ? signals.map((x) => <div className="stack-item" key={x.id}><div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("market-signals", x.id)}</div><strong>{humanize(x.signal_type)}</strong><p>{x.signal_description}</p>{x.possible_meaning && <small>{x.possible_meaning}</small>}</div>) : <p className="muted">{failedSections.has("signals") ? "Could not load market signals right now -- try refreshing." : "No linked market signals currently available."}</p>}<Disclaimer>{MARKET_DISCLAIMER}</Disclaimer></article>
        <article className="card insight-card insight-card-quality"><h3>✅ Quality readiness</h3>{quality.length ? quality.map((x) => <div className="stack-item" key={x.id}><div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("quality-signals", x.id)}</div><strong>{humanize(x.quality_status) || "Quality observation"}</strong><p>Moisture: {humanize(x.moisture_status) || "—"} · Storage readiness: {humanize(x.storage_readiness) || "—"}</p>{x.risk_note && <small>{x.risk_note}</small>}</div>) : <p className="muted">{failedSections.has("quality") ? "Could not load quality readiness right now -- try refreshing." : "No quality observation currently available."}</p>}</article>
        <article className="card insight-card insight-card-buying"><h3>🛒 Buying zone</h3>{zones.length ? zones.map((x) => { const today = new Date().toISOString().slice(0, 10); const outOfSeason = x.valid_from && x.valid_to && (today < x.valid_from || today > x.valid_to); return <div className="stack-item" key={x.id}><div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("buying-zones", x.id)}</div><strong>{money(x.price_low)} – {money(x.price_high)}</strong><p>{x.reason}</p><small>Confidence: {x.confidence}</small>{outOfSeason && <small className="season-note">Not currently in season — active {shortDate(x.valid_from)} to {shortDate(x.valid_to)}</small>}</div>; }) : <p className="muted">{failedSections.has("zones") ? "Could not load buying zone right now -- try refreshing." : "No buying-zone observation currently available."}</p>}</article>
        <article className="card insight-card insight-card-sellwatch"><h3>📈 Sell-watch window</h3>{sellWatch.length ? sellWatch.map((x) => { return <div className="stack-item" key={x.id}><div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("sell-watch", x.id)}</div><strong>{x.start_period}{x.end_period ? ` – ${x.end_period}` : ""}</strong><p>{x.observation}</p><small>Confidence: {x.confidence}</small></div>; }) : <p className="muted">{failedSections.has("sellWatch") ? "Could not load sell-watch window right now -- try refreshing." : "No sell-watch observation currently available."}</p>}</article>
        <article className="card insight-card insight-card-storage"><h3>📦 Storage suitability</h3>{storage.length ? storage.map((x) => <div className="stack-item" key={x.id}><div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("storage", x.id)}</div><strong>{humanize(x.suitability_status)}</strong><p>{x.summary || x.quality_storage_notes || "No summary supplied."}</p><small>Spoilage risk: {x.spoilage_risk || "—"} · Buyer availability: {x.buyer_availability || "—"}</small></div>) : <p className="muted">{failedSections.has("storage") ? "Could not load storage suitability right now -- try refreshing." : "No storage-suitability observation currently available."}</p>}<Disclaimer>{STORAGE_DISCLAIMER}</Disclaimer></article>
        <article className="card insight-card insight-card-costs"><h3>💰 Cost breakdown</h3>{costs.length ? costs.map((x) => {
          return <div className="stack-item" key={x.id}>
            <div className="stack-item-head"><span className="eyebrow">{marketLabel(x.market_id)}</span>{editLink("costs", x.id)}</div>
            <CostCalculator breakdown={x} />
            <p className="cost-reference-label">Reference breakdown (Unit not recorded)</p>
            <p>Purchase reference: {money(x.purchase_price_reference)} · Additional costs: {money(x.total_additional_cost)}</p>
            <small>Transport {money(x.transport)} · Warehouse {money(x.warehouse)} · Market charges {money(x.market_charges)}</small>
          </div>;
        }) : <p className="muted">{failedSections.has("costs") ? "Could not load cost breakdown right now -- try refreshing." : "No cost breakdown currently available for this commodity."}</p>}</article>
      </div>}
    </PremiumGate>
    </> : !error && <div className="status-box">No active {name} commodity is available.</div>}
  </section>;
}
