import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PriceCard } from "../components/PriceCard";
import { useCommodityMarketPairs } from "../hooks/useCommodityMarketPairs";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { usePreferences } from "../context/PreferencesContext";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate } from "../types/api";

const AUTO_REFRESH_MS = 60_000;

export function PricesPage() {
  const { dataSaver } = usePreferences();
  useDocumentTitle("Current Prices");
  const [searchParams] = useSearchParams();
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState(() => searchParams.get("commodity") || "");
  const [market, setMarket] = useState(() => searchParams.get("market") || "");
  const commodityMarketPairs = useCommodityMarketPairs();
  const availableMarkets = commodity && commodityMarketPairs.has(commodity)
    ? markets.filter((item) => commodityMarketPairs.get(commodity)!.has(item.name))
    : markets;
  const [movement, setMovement] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filtersLoading, setFiltersLoading] = useState(true);

  const load = async (params?: { commodity?: string; market?: string; movement?: string }, silent = false) => {
    if (!silent) { setLoading(true); setError(""); }
    const query = new URLSearchParams();
    if (params?.commodity) query.set("commodity", params.commodity);
    if (params?.market) query.set("market", params.market);
    if (params?.movement) query.set("movement", params.movement);
    try {
      const data = await apiFetch<PriceUpdate[]>(`/price-updates${query.size ? `?${query}` : ""}`);
      setItems(data);
      if (!silent) setError("");
    } catch (err) {
      if (!silent) setError((err as Error).message);
    } finally {
      if (!silent) setLoading(false);
    }
  };

  useEffect(() => {
    void load({ commodity, market });
    void Promise.all([
      apiFetch<Commodity[]>("/commodities"),
      apiFetch<Market[]>("/markets"),
    ]).then(([commodityItems, marketItems]) => {
      setCommodities(commodityItems);
      setMarkets(marketItems);
    }).catch(() => undefined).finally(() => setFiltersLoading(false));
  }, []);

  // Silently keep the list current while it's open, so an admin's new/edited price
  // shows up without the user needing to reload -- skipped under Data saver, since
  // repeated background fetches cost mobile data that toggle exists to avoid.
  useEffect(() => {
    if (dataSaver) return;
    const interval = setInterval(() => { void load({ commodity, market, movement }, true); }, AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [dataSaver, commodity, market, movement]);

  const submit = (event: FormEvent) => { event.preventDefault(); void load({ commodity, market, movement }); };
  const clear = () => { setCommodity(""); setMarket(""); setMovement(""); void load(); };
  const changeCommodity = (value: string) => {
    setCommodity(value);
    if (market && value && commodityMarketPairs.has(value) && !commodityMarketPairs.get(value)!.has(market)) setMarket("");
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Latest approved records</span><h1>Prices</h1><p>Search current commodity price ranges by commodity, market and movement.</p></div>
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select value={commodity} onChange={(e) => changeCommodity(e.target.value)}><option value="">Choose a commodity</option>{commodities.map((item) => <option key={item.id}>{item.name}</option>)}</select></label>
      <label>Market<select value={market} onChange={(e) => setMarket(e.target.value)}><option value="">Choose a market</option>{availableMarkets.map((item) => <option key={item.id}>{item.name}</option>)}</select>{commodity && availableMarkets.length < markets.length && <small className="muted">{commodity} is only tracked at {availableMarkets.length} market{availableMarkets.length === 1 ? "" : "s"} here.</small>}</label>
      <label>Movement<select value={movement} onChange={(e) => setMovement(e.target.value)}><option value="">Any movement</option><option value="up">Up</option><option value="down">Down</option><option value="stable">Stable</option><option value="unknown">Unknown</option></select></label>
      <div className="filter-actions"><button className="button button-small" type="submit" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Apply"}</button><button className="button button-ghost button-small" type="button" onClick={clear} disabled={loading}>Clear</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {loading || filtersLoading ? <LoadingSpinner label="Loading approved prices…" /> : items.length ? <div className="card-grid">{items.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No current prices found{commodity ? ` for ${commodity}` : ""}{market ? ` at ${market}` : ""}. Try clearing the filters or check back soon for new records.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
