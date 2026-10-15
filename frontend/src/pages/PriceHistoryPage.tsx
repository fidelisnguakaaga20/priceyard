import { FormEvent, useEffect, useState } from "react";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { PriceTrendChart } from "../components/PriceTrendChart";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { measurementLabel } from "../lib/priceSeries.mjs";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate } from "../types/api";
import { confidenceClass, money, movementIcon, shortDate } from "../utils";

const PAGE_SIZE = 100;

export function PriceHistoryPage() {
  useDocumentTitle("Price History");
  const { token, hasFullAccess, loading: authLoading } = useAuth();
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const [timeOfDay, setTimeOfDay] = useState("");
  const [filter, setFilter] = useState("");
  const [page, setPage] = useState(1);
  const [attempt, setAttempt] = useState(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const controller = new AbortController();
    if (authLoading || !token || !hasFullAccess) { setItems([]); setLoading(false); return; }
    setLoading(true);
    setItems([]);
    setError("");
    const query = new URLSearchParams(filter);
    query.set("page", String(page));
    query.set("page_size", String(PAGE_SIZE));
    void apiFetch<PriceUpdate[]>(`/price-updates/history?${query}`, { signal: controller.signal }, token)
      .then((records) => { if (!controller.signal.aborted) setItems(records); })
      .catch((err: Error) => { if (!controller.signal.aborted) setError(err.message); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [authLoading, hasFullAccess, token, filter, page, attempt]);

  useEffect(() => {
    let active = true;
    void Promise.allSettled([apiFetch<Commodity[]>("/commodities"), apiFetch<Market[]>("/markets")])
      .then(([commodityResult, marketResult]) => {
        if (!active) return;
        if (commodityResult.status === "fulfilled") setCommodities(commodityResult.value);
        if (marketResult.status === "fulfilled") setMarkets(marketResult.value);
      });
    return () => { active = false; };
  }, []);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const query = new URLSearchParams();
    if (commodity) query.set("commodity_id", commodity);
    if (market) query.set("market_id", market);
    if (timeOfDay) query.set("time_of_day", timeOfDay);
    setFilter(query.toString());
    setPage(1);
    setAttempt((value) => value + 1);
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Approved observations</span><h1>Price history</h1><p>Charts keep markets and recorded measurements separate. Dates use Nigerian local time.</p></div>
    {authLoading ? <LoadingSpinner label="Checking history access…" /> : !hasFullAccess ? <PremiumGate><></></PremiumGate> : <>
      <form className="filter-bar" onSubmit={submit}>
        <label>Commodity<select value={commodity} onChange={(event) => setCommodity(event.target.value)}><option value="">All commodities</option>{commodities.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></label>
        <label>Market<select value={market} onChange={(event) => setMarket(event.target.value)}><option value="">All markets</option>{markets.map((item) => <option value={item.id} key={item.id}>{item.name}{item.state ? ` (${item.state})` : ""}</option>)}</select></label>
        <label>Time of day<select value={timeOfDay} onChange={(event) => setTimeOfDay(event.target.value)}><option value="">Any time</option>{["morning", "afternoon", "evening", "closing"].map((value) => <option key={value}>{value}</option>)}</select></label>
        <div className="filter-actions"><button className="button button-small" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Search history"}</button></div>
      </form>
      {loading ? <LoadingSpinner label="Loading price history…" /> : error ? <div className="status-box error">{error}<button className="button button-small" onClick={() => setAttempt((value) => value + 1)}>Retry</button></div> : <>
        <p className="muted">Page {page}. Charts show comparable observations on this page.</p>
        <PriceTrendChart items={items} />
        <div className="table-wrap history-table-view"><table>
          <thead><tr><th>Date/time</th><th>Commodity / measurement</th><th>Market</th><th>Range</th><th>Previous</th><th>Movement</th><th>Status</th><th>Meaning / action</th></tr></thead>
          <tbody>{items.map((item) => <tr key={item.id}>
            <td>{shortDate(item.update_date_time)}<small>{item.time_of_day || ""}</small></td>
            <td>{item.commodity.name}<small>{measurementLabel(item)}</small></td><td>{item.market.name}</td>
            <td>{money(item.price_low)} – {money(item.price_high)}</td><td>{item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</td>
            <td>{item.movement}</td><td>{item.confidence_level}{item.is_outdated && " · outdated"}</td>
            <td><strong>{item.suggested_action || "No action supplied"}</strong><small>{item.possible_meaning || ""}</small></td>
          </tr>)}</tbody>
        </table></div>
        <div className="history-card-list">{items.map((item) => <article className="card" key={item.id}>
          <div className="card-row"><div><span className="eyebrow">{item.market.name}</span><h3>{item.commodity.name}</h3></div><span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)} {item.movement}</span></div>
          <p className="price-range">{money(item.price_low)} – {money(item.price_high)}</p><p className="muted">{measurementLabel(item)}</p>
          <p>Previous: {item.previous_price_low !== null ? `${money(item.previous_price_low)} – ${money(item.previous_price_high)}` : "Not confirmed"}</p>
          <div className="mini-grid"><span><strong>Status</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span>{item.is_outdated && " · outdated"}</span><span><strong>Date/time</strong>{shortDate(item.update_date_time)}</span></div>
          {(item.possible_meaning || item.suggested_action) && <div className="guidance"><p>{item.possible_meaning}</p><strong>{item.suggested_action}</strong></div>}
        </article>)}</div>
        {!items.length && <div className="status-box">No approved observations on this page. Try previous pages or different filters.</div>}
      </>}
      <div className="button-row"><button className="button button-secondary button-small" disabled={loading || page === 1} onClick={() => setPage((value) => value - 1)}>Previous page</button><button className="button button-small" disabled={loading || items.length < PAGE_SIZE} onClick={() => setPage((value) => value + 1)}>Next page</button></div>
    </>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
