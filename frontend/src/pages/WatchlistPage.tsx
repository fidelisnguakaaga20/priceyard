import { FormEvent, useEffect, useMemo, useState } from "react";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../services/api";
import type { Commodity, Market, WatchlistItem } from "../types/api";

export function WatchlistPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<WatchlistItem[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodityId, setCommodityId] = useState("");
  const [marketId, setMarketId] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [removingId, setRemovingId] = useState<number | null>(null);

  const load = async (showLoader = true) => {
    if (!token) return;
    if (showLoader) setLoading(true);
    try {
      const [watchlistItems, commodityItems, marketItems] = await Promise.all([
        apiFetch<WatchlistItem[]>("/watchlist", {}, token),
        apiFetch<Commodity[]>("/commodities"),
        apiFetch<Market[]>("/markets"),
      ]);
      setItems(watchlistItems);
      setCommodities(commodityItems);
      setMarkets(marketItems);
      setError("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      if (showLoader) setLoading(false);
    }
  };

  useEffect(() => { void load(); }, [token]);

  const commodityMap = useMemo(() => new Map(commodities.map((x) => [x.id, x.name])), [commodities]);
  const marketMap = useMemo(() => new Map(markets.map((x) => [x.id, x.name])), [markets]);

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
    } catch (err) {
      setError((err as Error).message);
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
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setRemovingId(null);
    }
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Your saved interests</span><h1>Watchlist</h1><p>Save a commodity, a market, or both. Target-price alerts remain deferred.</p></div>
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select value={commodityId} onChange={(e) => setCommodityId(e.target.value)}><option value="">No commodity</option>{commodities.filter((x) => x.is_active).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
      <label>Market<select value={marketId} onChange={(e) => setMarketId(e.target.value)}><option value="">No market</option>{markets.filter((x) => x.is_active).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</select></label>
      <div className="filter-actions"><button className="button button-small" disabled={saving || loading}>{saving ? <ButtonSpinner label="Please wait…" /> : "Save item"}</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <LoadingSpinner label="Loading your watchlist…" /> : <>
      <div className="watchlist-grid">{items.map((item) => <article className="card" key={item.id}><span className="eyebrow">Saved item</span><h3>{item.commodity_id ? commodityMap.get(item.commodity_id) || `Commodity #${item.commodity_id}` : "All commodities"}</h3><p>{item.market_id ? marketMap.get(item.market_id) || `Market #${item.market_id}` : "No market restriction"}</p><button className="button button-danger button-small" disabled={removingId !== null} onClick={() => void remove(item.id)}>{removingId === item.id ? <ButtonSpinner label="Please wait…" /> : "Remove"}</button></article>)}</div>
      {!items.length && !error && <div className="status-box">Your watchlist is empty. Save a commodity or market above to keep an eye on it here.</div>}
    </>}
  </section>;
}

