import { FormEvent, useEffect, useState } from "react";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";
import { confidenceClass, money, movementIcon, shortDate } from "../utils";

export function PriceHistoryPage() {
  useDocumentTitle("Price History");
  const { token, hasFullAccess, loading: authLoading } = useAuth();
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodity, setCommodity] = useState("Egusi");
  const [market, setMarket] = useState("");
  const [timeOfDay, setTimeOfDay] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const load = async () => {
    if (!token || !hasFullAccess) {
      setItems([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    const query = new URLSearchParams();
    if (commodity) query.set("commodity", commodity);
    if (market) query.set("market", market);
    if (timeOfDay) query.set("time_of_day", timeOfDay);

    try {
      setItems(await apiFetch<PriceUpdate[]>(`/price-updates/history?${query}`, {}, token));
      setError("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (!authLoading && hasFullAccess) void load();
  }, [authLoading, hasFullAccess, token]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void load();
  };

  return <section className="page page-section">
    <div className="page-title">
      <span className="eyebrow">Chronological records</span>
      <h1>Price history</h1>
      <p>Review approved historical ranges, movement and same-day market timing.</p>
    </div>

    {authLoading ? <LoadingSpinner label="Checking price-history access…" /> : !hasFullAccess ? <PremiumGate><></></PremiumGate> : <>
      <form className="filter-bar" onSubmit={submit}>
        <label>Commodity<input value={commodity} onChange={(e) => setCommodity(e.target.value)} /></label>
        <label>Market<input value={market} onChange={(e) => setMarket(e.target.value)} placeholder="Optional" /></label>
        <label>Time of day<select value={timeOfDay} onChange={(e) => setTimeOfDay(e.target.value)}><option value="">Any time</option><option>morning</option><option>afternoon</option><option>evening</option><option>closing</option></select></label>
        <div className="filter-actions"><button className="button button-small" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Search history"}</button></div>
      </form>

      {loading ? <LoadingSpinner label="Loading price history…" /> : error ? <div className="status-box error">{error}</div> : <>
        <div className="table-wrap history-table-view">
          <table>
            <thead><tr><th>Date/time</th><th>Commodity</th><th>Market</th><th>Range</th><th>Previous</th><th>Movement</th><th>Confidence</th><th>Meaning / action</th></tr></thead>
            <tbody>{items.map((item) => <tr key={item.id}>
              <td>{shortDate(item.update_date_time)}<small>{item.time_of_day || ""}</small></td>
              <td>{item.commodity.name}</td>
              <td>{item.market.name}</td>
              <td>{money(item.price_low)} – {money(item.price_high)}</td>
              <td>{item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "—"}</td>
              <td><span className={`movement movement-${item.movement}`}>{item.movement}</span></td>
              <td>{item.confidence_level}</td>
              <td><strong>{item.suggested_action || "Watch"}</strong><small>{item.possible_meaning || "—"}</small></td>
            </tr>)}</tbody>
          </table>
        </div>
        <div className="history-card-list">
          {items.map((item) => <article className="card" key={item.id}>
            <div className="card-row"><div><span className="eyebrow">{item.market.name}</span><h3>{item.commodity.name}</h3></div><span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span></div>
            <p className="price-range">{money(item.price_low)} – {money(item.price_high)}</p>
            <p className="muted">Previous: {item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</p>
            <div className="mini-grid">
              <span><strong>Confidence</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span></span>
              <span><strong>Date/time</strong>{shortDate(item.update_date_time)}{item.time_of_day ? ` · ${item.time_of_day}` : ""}</span>
            </div>
            <div className="guidance"><div><span>Possible Meaning</span><p>{item.possible_meaning || "No observation supplied."}</p></div><div><span>Suggested Action</span><strong>{item.suggested_action || "Watch"}</strong></div></div>
          </article>)}
        </div>
        {!items.length && <div className="status-box">No history records match the current filters.</div>}
      </>}
    </>}

    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
