import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PriceCard } from "../components/PriceCard";
import { useAuth } from "../context/AuthContext";
import { usePreferences } from "../context/PreferencesContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate } from "../types/api";

export function PricesPage() {
  useDocumentTitle("Current Prices");
  const { dataSaver } = usePreferences();
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const filterQuery = searchParams.toString();
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState(searchParams.get("commodity_id") || searchParams.get("commodity") || "");
  const [market, setMarket] = useState(searchParams.get("market_id") || searchParams.get("market") || "");
  const [movement, setMovement] = useState(searchParams.get("movement") || "");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filtersLoading, setFiltersLoading] = useState(true);
  const generation = useRef(0);
  const request = useRef<AbortController>();

  const refreshOptions = useCallback(async () => {
    const results = await Promise.allSettled([
      apiFetch<Commodity[]>("/commodities"), apiFetch<Market[]>("/markets"),
    ]);
    if (results[0].status === "fulfilled") setCommodities(results[0].value);
    if (results[1].status === "fulfilled") setMarkets(results[1].value);
    setFiltersLoading(false);
  }, []);

  const load = useCallback(async (silent = false) => {
    request.current?.abort();
    const controller = new AbortController();
    request.current = controller;
    const id = ++generation.current;
    if (!silent) { setLoading(true); setItems([]); }
    try {
      const data = await apiFetch<PriceUpdate[]>(`/price-updates${filterQuery ? `?${filterQuery}` : ""}`, { signal: controller.signal }, token);
      if (id !== generation.current) return;
      setItems(data);
      setError("");
    } catch (err) {
      if (id === generation.current && !controller.signal.aborted) setError((err as Error).message);
    } finally {
      if (id === generation.current) setLoading(false);
    }
  }, [filterQuery, token]);

  useEffect(() => {
    const values = new URLSearchParams(filterQuery);
    setCommodity(values.get("commodity_id") || values.get("commodity") || "");
    setMarket(values.get("market_id") || values.get("market") || "");
    setMovement(values.get("movement") || "");
    void load();
    return () => { ++generation.current; request.current?.abort(); };
  }, [filterQuery, load]);
  useEffect(() => { void refreshOptions(); }, [refreshOptions]);
  useEffect(() => {
    setCommodity((value) => String(commodities.find((item) => item.name === value)?.id ?? value));
    setMarket((value) => String(markets.find((item) => item.name === value)?.id ?? value));
  }, [commodities, markets]);
  useEffect(() => {
    if (dataSaver) return;
    const timer = setInterval(() => { void load(true); void refreshOptions(); }, 60_000);
    return () => clearInterval(timer);
  }, [dataSaver, load, refreshOptions]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    const query = new URLSearchParams();
    if (commodity) query.set(/^\d+$/.test(commodity) ? "commodity_id" : "commodity", commodity);
    if (market) query.set(/^\d+$/.test(market) ? "market_id" : "market", market);
    if (movement) query.set("movement", movement);
    if (query.toString() === filterQuery) void load();
    else setSearchParams(query);
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Latest approved records</span><h1>Prices</h1><p>Compare recorded quantities and specifications before interpreting a price difference.</p></div>
    <form className="filter-bar" onSubmit={submit}>
      <label>Commodity<select value={commodity} onChange={(event) => setCommodity(event.target.value)}><option value="">All commodities</option>{commodities.map((item) => <option value={item.id} key={item.id}>{item.name}</option>)}</select></label>
      <label>Market<select value={market} onChange={(event) => setMarket(event.target.value)}><option value="">All markets</option>{markets.map((item) => <option value={item.id} key={item.id}>{item.name}{item.state ? ` (${item.state})` : ""}</option>)}</select></label>
      <label>Movement<select value={movement} onChange={(event) => setMovement(event.target.value)}><option value="">Any movement</option>{["up", "down", "stable", "unknown"].map((value) => <option key={value}>{value}</option>)}</select></label>
      <div className="filter-actions"><button className="button button-small" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Apply"}</button><button className="button button-ghost button-small" type="button" onClick={() => { if (!filterQuery) void load(); else setSearchParams({}); }} disabled={loading}>Clear</button></div>
    </form>
    {error && <div className="status-box error" role="status">Could not refresh prices: {error}{items.length > 0 && " Showing the previously loaded observations."}<button className="button button-small" onClick={() => void load()}>Retry</button></div>}
    {loading || filtersLoading ? <LoadingSpinner label="Loading approved prices…" /> : items.length ? <div className="card-grid">{items.map((item) => <PriceCard key={item.id} item={item} />)}</div> : !error && <div className="status-box">No current prices match these filters. Clear them or check back for new approved observations.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
