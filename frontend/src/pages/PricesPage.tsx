import { FormEvent, useEffect, useState } from "react";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { PriceCard } from "../components/PriceCard";
import { apiFetch } from "../services/api";
import type { Market, PriceUpdate } from "../types/api";

export function PricesPage() {
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const [movement, setMovement] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

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

  useEffect(() => { void load(); apiFetch<Market[]>("/markets").then(setMarkets).catch(() => undefined); }, []);

  const submit = (event: FormEvent) => { event.preventDefault(); void load({ commodity, market, movement }); };
  const clear = () => { setCommodity(""); setMarket(""); setMovement(""); void load(); };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Latest approved records</span><h1>Prices</h1><p>Search current commodity price ranges by commodity, market and movement.</p></div>
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<input value={commodity} onChange={(e) => setCommodity(e.target.value)} placeholder="Egusi" /></label>
      <label>Market<select value={market} onChange={(e) => setMarket(e.target.value)}><option value="">All markets</option>{markets.filter((m) => m.is_active).map((m) => <option key={m.id}>{m.name}</option>)}</select></label>
      <label>Movement<select value={movement} onChange={(e) => setMovement(e.target.value)}><option value="">Any movement</option><option value="up">Up</option><option value="down">Down</option><option value="stable">Stable</option><option value="unknown">Unknown</option></select></label>
      <div className="filter-actions"><button className="button button-small" type="submit">Apply</button><button className="button button-ghost button-small" type="button" onClick={clear}>Clear</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <div className="status-box">Loading approved prices…</div> : items.length ? <div className="card-grid">{items.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No approved price updates match these filters.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
