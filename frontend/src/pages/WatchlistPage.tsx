import { FormEvent, useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PushAlertPrompt } from "../components/PushAlertPrompt";
import { useAuth } from "../context/AuthContext";
import { useCommodityMarketPairs } from "../hooks/useCommodityMarketPairs";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate, WatchlistItem } from "../types/api";
import { agingClass, money, movementIcon, relativeTime } from "../utils";

const FEEDBACK_PROMPT_KEY = "priceyard_feedback_prompted";

export function WatchlistPage() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [commodityId, setCommodityId] = useState("");
  const [marketId, setMarketId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [showFeedbackPrompt, setShowFeedbackPrompt] = useState(false);
  const commodityMarketPairs = useCommodityMarketPairs();

  const load = async (showLoader = true) => {
    if (!token) return;
    if (showLoader) setLoading(true);
    try {
      const [watchlistItems, commodityItems, marketItems, priceItems] = await Promise.all([
        apiFetch<WatchlistItem[]>("/watchlist", {}, token),
        apiFetch<Commodity[]>("/commodities"),
        apiFetch<Market[]>("/markets"),
        apiFetch<PriceUpdate[]>("/price-updates"),
      ]);
      setItems(watchlistItems);
      setCommodities(commodityItems);
      setMarkets(marketItems);
      setPrices(priceItems);
      setError("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [token]);

  useEffect(() => {
    if (items.length < 2) return;
    try {
      if (localStorage.getItem(FEEDBACK_PROMPT_KEY) === "1") return;
    } catch { /* ignore */ }
    setShowFeedbackPrompt(true);
  }, [items.length]);

  const dismissFeedbackPrompt = () => {
    setShowFeedbackPrompt(false);
    try { localStorage.setItem(FEEDBACK_PROMPT_KEY, "1"); } catch { /* ignore */ }
  };

  const commodityMap = useMemo(() => new Map(commodities.map((x) => [x.id, x.name])), [commodities]);
  const marketMap = useMemo(() => new Map(markets.map((x) => [x.id, x.name])), [markets]);

  const findPriceFor = (item: WatchlistItem): PriceUpdate | undefined => {
    if (item.commodity_id && item.market_id) {
      return prices.find((p) => p.commodity_id === item.commodity_id && p.market_id === item.market_id);
    }
    if (item.commodity_id) return prices.find((p) => p.commodity_id === item.commodity_id);
    if (item.market_id) return prices.find((p) => p.market_id === item.market_id);
    return undefined;
  };

  const selectedCommodityName = commodityId ? commodityMap.get(Number(commodityId)) : undefined;
  const activeMarkets = markets.filter((x) => x.is_active);
  const availableMarkets = selectedCommodityName && commodityMarketPairs.has(selectedCommodityName)
    ? activeMarkets.filter((x) => commodityMarketPairs.get(selectedCommodityName)!.has(x.name))
    : activeMarkets;

  const changeCommodity = (value: string) => {
    setCommodityId(value);
    const name = value ? commodityMap.get(Number(value)) : undefined;
    const currentMarketName = marketId ? marketMap.get(Number(marketId)) : undefined;
    if (currentMarketName && name && commodityMarketPairs.has(name) && !commodityMarketPairs.get(name)!.has(currentMarketName)) {
      setMarketId("");
    }
  };

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || saving || (!commodityId && !marketId)) {
      if (!commodityId && !marketId) setError("Choose a commodity, a market, or both.");
      return;
    }
    setSaving(true);
    try {
      await apiFetch("/watchlist", {
        method: "POST",
        body: JSON.stringify({
          commodity_id: commodityId ? Number(commodityId) : null,
          market_id: marketId ? Number(marketId) : null,
        }),
      }, token);
      setCommodityId("");
      setMarketId("");
      await load(false);
      showToast("Added to your watchlist.");
    } catch (err) {
      setError((err as Error).message);
      showToast((err as Error).message, "error");
    } finally {
      setSaving(false);
    }
  };

  const remove = async (id: number) => {
    if (!token || removingId !== null) return;
    setRemovingId(id);
    try {
      await apiFetch(`/watchlist/${id}`, { method: "DELETE" }, token);
      await load(false);
      showToast("Removed from your watchlist.");
    } catch (err) {
      setError((err as Error).message);
      showToast((err as Error).message, "error");
    } finally {
      setRemovingId(null);
    }
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Your saved interests</span><h1>Watchlist</h1><p>Save a product, a market, or both — we'll email you whenever a new price is approved for it, so you don't have to keep checking back.</p></div>
    <PushAlertPrompt />
    {showFeedbackPrompt && (
      <div className="feedback-prompt">
        <span>Enjoying PriceYard so far? We'd love to hear from you.</span>
        <div className="feedback-prompt-actions">
          <Link className="button button-small" to="/feedback" onClick={dismissFeedbackPrompt}>Leave feedback</Link>
          <button type="button" className="text-link text-link-button" onClick={dismissFeedbackPrompt}>Not now</button>
        </div>
      </div>
    )}
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select value={commodityId} onChange={(e) => changeCommodity(e.target.value)}><option value="">Choose a commodity</option>{commodities.filter((x) => x.is_active).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
      <label>Market<select value={marketId} onChange={(e) => setMarketId(e.target.value)}><option value="">Choose a market</option>{availableMarkets.map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select>{selectedCommodityName && availableMarkets.length < activeMarkets.length && <small className="muted">{selectedCommodityName} is only tracked at {availableMarkets.length} market{availableMarkets.length === 1 ? "" : "s"} here.</small>}</label>
      <div className="filter-actions"><button className="button button-small" disabled={saving || loading}>{saving ? <ButtonSpinner label="Please wait…" /> : "Save item"}</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <LoadingSpinner label="Loading your watchlist…" /> : <>
      <div className="watchlist-grid">{items.map((item) => {
        const match = findPriceFor(item);
        return <article className="card" key={item.id}>
          <span className="eyebrow">Saved item</span>
          <h3>{item.commodity_id ? commodityMap.get(item.commodity_id) || `Commodity #${item.commodity_id}` : "All commodities"}</h3>
          <p className="muted">{item.market_id ? marketMap.get(item.market_id) || `Market #${item.market_id}` : "No market restriction"}</p>
          {match ? (
            <>
              <p className="price-range">{money(match.price_low)} – {money(match.price_high)}</p>
              <div className="mini-grid">
                <span><strong>Movement</strong><span className={`movement movement-${match.movement}`}>{movementIcon(match.movement)} {match.movement}</span></span>
                <span><strong>Updated</strong><span className={agingClass(match.update_date_time)}>{relativeTime(match.update_date_time)}</span></span>
              </div>
            </>
          ) : (
            <p className="muted">No current price yet.</p>
          )}
          <button className="button button-danger button-small" disabled={removingId !== null} onClick={() => void remove(item.id)}>{removingId === item.id ? <ButtonSpinner label="Please wait…" /> : "Remove"}</button>
        </article>;
      })}</div>
      {!items.length && !error && <div className="status-box">Your watchlist is empty. Save a commodity or market above to keep an eye on it here.</div>}
    </>}
  </section>;
}

