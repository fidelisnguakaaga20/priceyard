import { FormEvent, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { BackToFilters } from "../components/BackToFilters";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { PremiumGate } from "../components/PremiumGate";
import { PriceTrendChart } from "../components/PriceTrendChart";
import { useAuth } from "../context/AuthContext";
import { useHistoricalCommodityMarketPairs } from "../hooks/useCommodityMarketPairs";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import { addIdentityFilter, identityLabel, identityValue, nameSelection, selectedIdentity, selectionFromQuery } from "../services/priceIdentity";
import type { Commodity, Market, PriceUpdate } from "../types/api";
import { confidenceClass, money, movementIcon } from "../utils";

import { PRICE_TIME_LABEL, shortPriceDate } from "../utils/priceTime";

export function PriceHistoryPage() {
  useDocumentTitle("Price History");
  const { token, hasFullAccess, loading: authLoading } = useAuth();
  const [searchParams] = useSearchParams();
  const lastQuery = useRef(searchParams.toString());
  const filtersRef = useRef<HTMLFormElement>(null);
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState(() => searchParams.has("commodity_id") || searchParams.has("commodity")
    ? selectionFromQuery(searchParams, "commodity") : nameSelection("Egusi"));
  const [market, setMarket] = useState(() => selectionFromQuery(searchParams, "market"));
  const commodityMarketPairs = useHistoricalCommodityMarketPairs(hasFullAccess ? token : null);
  const commodityLabel = identityLabel(commodity, commodities);
  const marketLabel = identityLabel(market, markets);
  const availableMarkets = commodityLabel && commodityMarketPairs.has(commodityLabel)
    ? markets.filter((item) => commodityMarketPairs.get(commodityLabel)!.has(item.name))
    : markets;
  const [timeOfDay, setTimeOfDay] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const requestSequence = useRef(0);
  const activeAccess = useRef({ token, hasFullAccess });
  activeAccess.current = { token, hasFullAccess };

  const load = async (selection = { commodity, market, timeOfDay }) => {
    const sequence = ++requestSequence.current;
    if (!token || !hasFullAccess) {
      setItems([]);
      setLoading(false);
      return;
    }

    setLoading(true);
    setError("");
    const isCurrent = () => sequence === requestSequence.current && token === activeAccess.current.token && activeAccess.current.hasFullAccess;
    const query = new URLSearchParams();
    addIdentityFilter(query, "commodity", selectedIdentity(selection.commodity, commodities));
    addIdentityFilter(query, "market", selectedIdentity(selection.market, markets));
    if (selection.timeOfDay) query.set("time_of_day", selection.timeOfDay);

    try {
      const data = await apiFetch<PriceUpdate[]>(`/price-updates/history?${query}`, {}, token);
      if (!isCurrent()) return;
      setItems(data);
      setError("");
    } catch (err) {
      if (isCurrent()) setError((err as Error).message);
    } finally {
      if (isCurrent()) setLoading(false);
    }
  };

  useEffect(() => {
    let current = true;
    if (!authLoading && hasFullAccess) {
      const queryChanged = lastQuery.current !== searchParams.toString();
      lastQuery.current = searchParams.toString();
      const requestedCommodity = queryChanged
        ? searchParams.has("commodity_id") || searchParams.has("commodity")
          ? selectionFromQuery(searchParams, "commodity") : nameSelection("Egusi")
        : commodity;
      const requestedMarket = queryChanged ? selectionFromQuery(searchParams, "market") : market;
      const requestedTime = queryChanged ? "" : timeOfDay;
      setCommodity(requestedCommodity); setMarket(requestedMarket); setTimeOfDay(requestedTime);
      setLoading(true);
      void Promise.all([
        apiFetch<Commodity[]>("/commodities"),
        apiFetch<Market[]>("/markets"),
      ]).then(([commodityItems, marketItems]) => {
        if (!current) return;
        setCommodities(commodityItems);
        setMarkets(marketItems);
        const chosenCommodity = selectedIdentity(requestedCommodity, commodityItems);
        const chosenMarket = selectedIdentity(requestedMarket, marketItems);
        setCommodity(chosenCommodity); setMarket(chosenMarket);
        void load({ commodity: chosenCommodity, market: chosenMarket, timeOfDay: requestedTime });
      }).catch((err: Error) => { if (current) { setError(err.message); setLoading(false); } });
    } else if (!authLoading) {
      setItems([]); setError(""); setLoading(false);
    }
    return () => { current = false; requestSequence.current++; };
  }, [authLoading, hasFullAccess, token, searchParams]);

  useEffect(() => { window.scrollTo({ top: 0, behavior: "auto" }); }, [searchParams]);

  const submit = (event: FormEvent) => {
    event.preventDefault();
    void load();
  };

  const changeCommodity = (value: string) => {
    setCommodity(value);
    const label = identityLabel(value, commodities);
    if (market && label && commodityMarketPairs.has(label) && !commodityMarketPairs.get(label)!.has(marketLabel)) setMarket("");
  };

  return <section className="page page-section">
    <div className="page-title">
      <span className="eyebrow">All price records</span>
      <h1>Price history</h1>
      <p>Review approved historical ranges, movement and same-day market timing.</p>
      <p className="muted">{PRICE_TIME_LABEL}</p>
    </div>

    {authLoading ? <LoadingSpinner label="Checking price-history access…" /> : !hasFullAccess ? <PremiumGate><></></PremiumGate> : <>
      <form ref={filtersRef} className="filter-bar history-filters" onSubmit={submit}>
        <label>Commodity<select value={selectedIdentity(commodity, commodities)} onChange={(e) => changeCommodity(e.target.value)}><option value="">Choose a commodity</option>{commodities.map((item) => <option value={identityValue(item.id)} key={item.id}>{item.name}</option>)}</select></label>
        <label>Market<select value={selectedIdentity(market, markets)} onChange={(e) => setMarket(e.target.value)}><option value="">Choose a market</option>{availableMarkets.map((item) => <option value={identityValue(item.id)} key={item.id}>{item.name}</option>)}</select>{commodity && availableMarkets.length < markets.length && <small className="muted">{commodityLabel} is only tracked at {availableMarkets.length} market{availableMarkets.length === 1 ? "" : "s"} here.</small>}</label>
        <label>Time of day<select value={timeOfDay} onChange={(e) => setTimeOfDay(e.target.value)}><option value="">Any time</option><option>morning</option><option>afternoon</option><option>evening</option><option>closing</option></select></label>
        <div className="filter-actions"><button className="button button-small" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Search history"}</button></div>
      </form>
      <BackToFilters filtersRef={filtersRef} enabled={hasFullAccess && !authLoading} />

      {loading ? <LoadingSpinner label="Loading price history…" /> : error ? <div className="status-box error">{error}</div> : <>
        <PriceTrendChart items={items} />
        <div className="table-wrap history-table-view">
          <table>
            <thead><tr><th>Date/time</th><th>Commodity</th><th>Market</th><th>Range</th><th>Previous</th><th>Movement</th><th>Status</th><th>Meaning / action</th></tr></thead>
            <tbody>{items.map((item) => <tr key={item.id}>
              <td>{shortPriceDate(item.update_date_time)}<small>{item.time_of_day || ""}</small></td>
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
              <span><strong>Status</strong><span className={`confidence-badge ${confidenceClass(item.confidence_level)}`}>{item.confidence_level}</span></span>
              <span><strong>Date/time</strong>{shortPriceDate(item.update_date_time)}{item.time_of_day ? ` · ${item.time_of_day}` : ""}</span>
            </div>
            <div className="guidance"><div><span>Possible Meaning</span><p>{item.possible_meaning || "No observation supplied."}</p></div><div><span>Suggested Action</span><strong>{item.suggested_action || "Watch"}</strong></div></div>
          </article>)}
        </div>
        {!items.length && <div className="status-box">No history records found{commodity ? ` for ${commodityLabel}` : ""}{market ? ` at ${marketLabel}` : ""}. Try a different market, commodity, or time of day.</div>}
      </>}
    </>}

    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
