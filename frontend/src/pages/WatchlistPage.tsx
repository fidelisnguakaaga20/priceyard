import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PushAlertPrompt } from "../components/PushAlertPrompt";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { measurementLabel, matchesTargetBasis } from "../lib/priceSeries.mjs";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate, TargetDirection, WatchlistItem } from "../types/api";
import { money, relativeTime } from "../utils";

const FEEDBACK_PROMPT_KEY = "priceyard_feedback_prompted";
type Specification = { unit: string; bagSize: string; variant: string; grade: string };
const EMPTY_SPEC: Specification = { unit: "", bagSize: "", variant: "", grade: "" };
const payloadSpec = (spec: Specification) => ({ target_unit: spec.unit.trim() || null,
  target_bag_size: spec.bagSize.trim() || null, target_commodity_type: spec.variant.trim() || null,
  target_grade: spec.grade.trim() || null });

function TargetFields({ specification, setSpecification, prices }: {
  specification: Specification; setSpecification: (value: Specification) => void; prices: PriceUpdate[];
}) {
  return <>
    {prices.length > 0 && <label>Copy a recorded specification (optional)<select value="" onChange={(event) => {
      const selected = prices.find((item) => item.id === Number(event.target.value));
      if (selected) setSpecification({ unit: selected.unit, bagSize: selected.bag_size || "", variant: selected.commodity_type || "", grade: selected.grade || "" });
    }}><option value="">Choose a recorded quantity</option>{prices.filter((item) => item.bag_size).map((item) => <option value={item.id} key={item.id}>{measurementLabel(item)}</option>)}</select></label>}
    <label>Priced quantity<input required maxLength={100} placeholder="As recorded, e.g. 1 bag" value={specification.unit} onChange={(event) => setSpecification({ ...specification, unit: event.target.value })} /></label>
    <label>Bag/package specification<input required maxLength={100} placeholder="Record the known size; do not guess" value={specification.bagSize} onChange={(event) => setSpecification({ ...specification, bagSize: event.target.value })} /></label>
    <label>Commodity type (if recorded)<input maxLength={150} value={specification.variant} onChange={(event) => setSpecification({ ...specification, variant: event.target.value })} /></label>
    <label>Grade (if recorded)<input maxLength={100} value={specification.grade} onChange={(event) => setSpecification({ ...specification, grade: event.target.value })} /></label>
    <p className="muted">Your target matches this exact quantity, package, type and grade. Leave type/grade blank only for an unspecified observation.</p>
  </>;
}

function ConfirmExistingTarget({ item, commodities, markets, prices, confirm }: {
  item: WatchlistItem; commodities: Commodity[]; markets: Market[]; prices: PriceUpdate[];
  confirm: (id: number, payload: Record<string, unknown>) => Promise<void>;
}) {
  const [commodityId, setCommodityId] = useState(String(item.commodity_id || ""));
  const [marketId, setMarketId] = useState(String(item.market_id || ""));
  const [specification, setSpecification] = useState<Specification>(EMPTY_SPEC);
  const [busy, setBusy] = useState(false);
  return <form className="form-stack" onSubmit={async (event) => {
    event.preventDefault(); setBusy(true);
    try { await confirm(item.id, { commodity_id: Number(commodityId), market_id: Number(marketId),
      target_price: item.target_price, target_direction: item.target_direction, ...payloadSpec(specification) }); }
    finally { setBusy(false); }
  }}>
    <p className="status-box">This saved target is paused until its market and measurement are confirmed. Its existing price is preserved.</p>
    <label>Commodity<select required value={commodityId} onChange={(event) => { setCommodityId(event.target.value); setSpecification(EMPTY_SPEC); }}><option value="">Choose a commodity</option>{commodities.map((value) => <option value={value.id} key={value.id}>{value.name}</option>)}</select></label>
    <label>Market<select required value={marketId} onChange={(event) => { setMarketId(event.target.value); setSpecification(EMPTY_SPEC); }}><option value="">Choose a market</option>{markets.map((value) => <option value={value.id} key={value.id}>{value.name}{value.state ? ` (${value.state})` : ""}</option>)}</select></label>
    <TargetFields specification={specification} setSpecification={setSpecification} prices={prices.filter((price) => price.commodity_id === Number(commodityId) && price.market_id === Number(marketId))} />
    <button className="button button-small" disabled={busy}>{busy ? "Saving…" : "Confirm target measurement"}</button>
  </form>;
}

export function WatchlistPage() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [commodityId, setCommodityId] = useState("");
  const [marketId, setMarketId] = useState("");
  const [targetPrice, setTargetPrice] = useState("");
  const [targetDirection, setTargetDirection] = useState<TargetDirection>("at_or_below");
  const [specification, setSpecification] = useState<Specification>(EMPTY_SPEC);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [showFeedbackPrompt, setShowFeedbackPrompt] = useState(false);
  const generation = useRef(0);

  const load = useCallback(async (showLoader = true) => {
    if (!token) { setItems([]); setLoading(false); return; }
    const id = ++generation.current;
    if (showLoader) setLoading(true);
    const results = await Promise.allSettled([
      apiFetch<WatchlistItem[]>("/watchlist", {}, token), apiFetch<Commodity[]>("/commodities"),
      apiFetch<Market[]>("/markets"), apiFetch<PriceUpdate[]>("/price-updates"),
    ]);
    if (id !== generation.current) return;
    if (results[0].status === "fulfilled") setItems(results[0].value);
    if (results[1].status === "fulfilled") setCommodities(results[1].value);
    if (results[2].status === "fulfilled") setMarkets(results[2].value);
    if (results[3].status === "fulfilled") setPrices(results[3].value);
    const failed = results.find((result) => result.status === "rejected");
    setError(failed?.status === "rejected" ? `Some information could not load: ${failed.reason instanceof Error ? failed.reason.message : "Retry your connection."}` : "");
    setLoading(false);
  }, [token]);
  useEffect(() => { void load(); return () => { ++generation.current; }; }, [load]);
  useEffect(() => {
    if (items.length < 2) return;
    try { if (localStorage.getItem(FEEDBACK_PROMPT_KEY) === "1") return; } catch { return; }
    setShowFeedbackPrompt(true);
  }, [items.length]);
  const dismissFeedbackPrompt = () => { setShowFeedbackPrompt(false); try { localStorage.setItem(FEEDBACK_PROMPT_KEY, "1"); } catch { /* Optional preference. */ } };
  const commodityMap = useMemo(() => new Map(commodities.map((item) => [item.id, item.name])), [commodities]);
  const marketMap = useMemo(() => new Map(markets.map((item) => [item.id, item.name])), [markets]);
  const pairPrices = prices.filter((price) => price.commodity_id === Number(commodityId) && price.market_id === Number(marketId));

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || saving) return;
    if (!commodityId && !marketId) { setError("Choose a commodity, a market, or both."); return; }
    setSaving(true);
    try {
      const saved = await apiFetch<WatchlistItem>("/watchlist", { method: "POST", body: JSON.stringify({
        commodity_id: commodityId ? Number(commodityId) : null, market_id: marketId ? Number(marketId) : null,
        target_price: targetPrice === "" ? null : Number(targetPrice), target_direction: targetPrice === "" ? null : targetDirection,
        ...(targetPrice === "" ? {} : payloadSpec(specification)),
      }) }, token);
      setItems((records) => [saved, ...records]);
      setCommodityId(""); setMarketId(""); setTargetPrice(""); setSpecification(EMPTY_SPEC);
      setError(""); showToast("Added to your watchlist.");
    } catch (err) { setError((err as Error).message); showToast((err as Error).message, "error"); }
    finally { setSaving(false); }
  };
  const confirm = async (id: number, payload: Record<string, unknown>) => {
    if (!token) return;
    try {
      const saved = await apiFetch<WatchlistItem>(`/watchlist/${id}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
      setItems((records) => records.map((item) => item.id === id ? saved : item)); setError("");
      showToast("Target measurement confirmed.");
    } catch (err) { setError((err as Error).message); showToast((err as Error).message, "error"); }
  };
  const remove = async (id: number) => {
    if (!token || removingId !== null) return;
    setRemovingId(id);
    try { await apiFetch(`/watchlist/${id}`, { method: "DELETE" }, token); setItems((records) => records.filter((item) => item.id !== id)); showToast("Removed from your watchlist."); }
    catch (err) { setError((err as Error).message); }
    finally { setRemovingId(null); }
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Your saved interests</span><h1>Watchlist</h1><p>Save a commodity, market or exact pair. A price target requires a recorded measurement. Alerts describe observed ranges and do not guarantee a transaction price.</p></div>
    <PushAlertPrompt />
    {showFeedbackPrompt && <div className="feedback-prompt"><span>How is PriceYard working for you?</span><div className="feedback-prompt-actions"><Link className="button button-small" to="/feedback" onClick={dismissFeedbackPrompt}>Leave feedback</Link><button type="button" className="text-link text-link-button" onClick={dismissFeedbackPrompt}>Not now</button></div></div>}
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select required={targetPrice !== ""} value={commodityId} onChange={(event) => { setCommodityId(event.target.value); setSpecification(EMPTY_SPEC); }}><option value="">Any commodity</option>{commodities.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></label>
      <label>Market<select required={targetPrice !== ""} value={marketId} onChange={(event) => { setMarketId(event.target.value); setSpecification(EMPTY_SPEC); }}><option value="">Any market</option>{markets.map((item) => <option value={item.id} key={item.id}>{item.name}{item.state ? ` (${item.state})` : ""}</option>)}</select></label>
      <label>Target price in NGN (optional)<input type="number" min="0" step="0.01" value={targetPrice} onChange={(event) => setTargetPrice(event.target.value)} /></label>
      {targetPrice !== "" && <><label>Direction<select value={targetDirection} onChange={(event) => setTargetDirection(event.target.value as TargetDirection)}><option value="at_or_below">Range drops to or below target</option><option value="at_or_above">Range rises to or above target</option></select></label><TargetFields specification={specification} setSpecification={setSpecification} prices={pairPrices} /></>}
      <div className="filter-actions"><button className="button button-small" disabled={saving || loading}>{saving ? <ButtonSpinner label="Saving…" /> : "Save item"}</button></div>
    </form>
    {error && <div className="status-box error">{error}<button className="button button-small" onClick={() => void load()}>Retry</button></div>}
    {loading ? <LoadingSpinner label="Loading your watchlist…" /> : <div className="watchlist-grid">{items.map((item) => {
      const targeted = item.target_price !== null;
      const matches = prices.filter((price) => (!item.commodity_id || price.commodity_id === item.commodity_id) && (!item.market_id || price.market_id === item.market_id) && (!targeted || matchesTargetBasis(item, price)));
      const reached = targeted && matches.some((price) => item.target_direction === "at_or_above" ? Number(price.price_high) >= Number(item.target_price) : Number(price.price_low) <= Number(item.target_price));
      return <article className="card" key={item.id}>
        <span className="eyebrow">Saved item</span><h3>{item.commodity_id ? commodityMap.get(item.commodity_id) || `Commodity #${item.commodity_id}` : "All commodities"}</h3><p>{item.market_id ? marketMap.get(item.market_id) || `Market #${item.market_id}` : "Any market"}</p>
        {targeted && <p>{item.target_direction === "at_or_above" ? "At or above" : "At or below"} {money(item.target_price)}{reached && " · Observed range includes your target"}</p>}
        {targeted && !item.target_measurement_confirmed && <ConfirmExistingTarget item={item} commodities={commodities} markets={markets} prices={prices} confirm={confirm} />}
        {matches.slice(0, 3).map((price) => <div className="stack-item" key={price.id}><strong>{price.commodity.name} · {price.market.name}</strong><p>{money(price.price_low)} – {money(price.price_high)}</p><small>{measurementLabel(price)} · {relativeTime(price.update_date_time)}</small></div>)}
        {matches.length > 3 && <Link className="text-link" to="/prices">See all matching current observations</Link>}
        {!matches.length && <p className="muted">No current observation matches this saved scope and confirmed measurement.</p>}
        <button className="button button-danger button-small" disabled={removingId !== null} onClick={() => void remove(item.id)}>{removingId === item.id ? "Removing…" : "Remove"}</button>
      </article>;
    })}{!items.length && !error && <p className="status-box">Your watchlist is empty. Save an interest above.</p>}</div>}
  </section>;
}
