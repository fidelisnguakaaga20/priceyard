import { FormEvent, useEffect, useState } from "react";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PriceCard } from "../components/PriceCard";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate } from "../types/api";

export function PricesPage() {
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const [movement, setMovement] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filtersLoading, setFiltersLoading] = useState(true);

  const load = async (params?: { commodity?: string; market?: string; movement?: string }) => {
    setLoading(true); setError("");
    const query = new URLSearchParams();
    if (params?.commodity) query.set("commodity", params.commodity);
    if (params?.market) query.set("market", params.market);
    if (params?.movement) query.set("movement", params.movement);
    try { setItems(await apiFetch<PriceUpdate[]>(`/price-updates${query.size ? `?${query}` : ""}`)); }
    catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    void load();
    void Promise.all([
      apiFetch<Commodity[]>("/commodities"),
      apiFetch<Market[]>("/markets"),
    ]).then(([commodityItems, marketItems]) => {
      setCommodities(commodityItems);
      setMarkets(marketItems);
    }).catch(() => undefined).finally(() => setFiltersLoading(false));
  }, []);

  const submit = (event: FormEvent) => { event.preventDefault(); void load({ commodity, market, movement }); };
  const clear = () => { setCommodity(""); setMarket(""); setMovement(""); void load(); };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Latest approved records</span><h1>Prices</h1><p>Search current commodity price ranges by commodity, market and movement.</p></div>
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select value={commodity} onChange={(e) => setCommodity(e.target.value)}><option value="">All commodities</option>{commodities.map((item) => <option key={item.id}>{item.name}</option>)}</select></label>
      <label>Market<select value={market} onChange={(e) => setMarket(e.target.value)}><option value="">All markets</option>{markets.map((item) => <option key={item.id}>{item.name}</option>)}</select></label>
      <label>Movement<select value={movement} onChange={(e) => setMovement(e.target.value)}><option value="">Any movement</option><option value="up">Up</option><option value="down">Down</option><option value="stable">Stable</option><option value="unknown">Unknown</option></select></label>
      <div className="filter-actions"><button className="button button-small" type="submit" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Apply"}</button><button className="button button-ghost button-small" type="button" onClick={clear} disabled={loading}>Clear</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {loading || filtersLoading ? <LoadingSpinner label="Loading approved prices…" /> : items.length ? <div className="card-grid">{items.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No approved price updates match these filters. Try clearing the filters or check back soon for new records.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
