import { FormEvent, useEffect, useState } from "react";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";
import { money, shortDate } from "../utils";

export function PriceHistoryPage() {
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodity, setCommodity] = useState("Egusi");
  const [market, setMarket] = useState("");
  const [timeOfDay, setTimeOfDay] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const load = async () => {
    setLoading(true);
    const q = new URLSearchParams();
    if (commodity) q.set("commodity", commodity);
    if (market) q.set("market", market);
    if (timeOfDay) q.set("time_of_day", timeOfDay);
    try { setItems(await apiFetch<PriceUpdate[]>(`/price-updates/history?${q}`)); setError(""); }
    catch (err) { setError((err as Error).message); }
    finally { setLoading(false); }
  };
  useEffect(() => { void load(); }, []);
  const submit = (event: FormEvent) => { event.preventDefault(); void load(); };

  return <section className="page page-section"><div className="page-title"><span className="eyebrow">Chronological records</span><h1>Price history</h1><p>Review approved historical ranges, movement and same-day market timing.</p></div>
    <form className="filter-bar" onSubmit={submit}><label>Commodity<input value={commodity} onChange={(e) => setCommodity(e.target.value)} /></label><label>Market<input value={market} onChange={(e) => setMarket(e.target.value)} placeholder="Optional" /></label><label>Time of day<select value={timeOfDay} onChange={(e) => setTimeOfDay(e.target.value)}><option value="">Any time</option><option>morning</option><option>afternoon</option><option>evening</option><option>closing</option></select></label><div className="filter-actions"><button className="button button-small" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Search history"}</button></div></form>
    {loading ? <LoadingSpinner label="Loading price history…" /> : error ? <div className="status-box error">{error}</div> : <div className="table-wrap"><table><thead><tr><th>Date/time</th><th>Commodity</th><th>Market</th><th>Range</th><th>Previous</th><th>Movement</th><th>Confidence</th><th>Meaning / action</th></tr></thead><tbody>{items.map((x) => <tr key={x.id}><td>{shortDate(x.update_date_time)}<small>{x.time_of_day || ""}</small></td><td>{x.commodity.name}</td><td>{x.market.name}</td><td>{money(x.price_low)} – {money(x.price_high)}</td><td>{x.previous_price_low !== null ? `${money(x.previous_price_low)} – ${money(x.previous_price_high)}` : "—"}</td><td><span className={`movement movement-${x.movement}`}>{x.movement}</span></td><td>{x.confidence_level}</td><td><strong>{x.suggested_action || "Watch"}</strong><small>{x.possible_meaning || "—"}</small></td></tr>)}</tbody></table>{!items.length && <div className="status-box">No history records match the current filters.</div>}</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
