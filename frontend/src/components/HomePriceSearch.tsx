import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { addIdentityFilter, identityValue } from "../services/priceIdentity";
import type { Commodity, Market, PriceUpdate } from "../types/api";
import "./HomePriceSearch.css";

/** Reuses the homepage's public catalogues; results use the existing price filters. */
export function HomePriceSearch({ commodities, markets, prices, loading, error }: {
  commodities: Commodity[]; markets: Market[]; prices: PriceUpdate[]; loading: boolean; error: boolean;
}) {
  const navigate = useNavigate();
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const availableMarkets = useMemo(() => {
    if (!commodity) return markets;
    const marketIds = new Set(prices.filter((item) => identityValue(item.commodity_id) === commodity).map((item) => item.market_id));
    return markets.filter((item) => marketIds.has(item.id));
  }, [commodity, markets, prices]);
  const selectedMarket = availableMarkets.some((item) => identityValue(item.id) === market) ? market : "";
  useEffect(() => {
    if (!loading && !error && market && !selectedMarket) setMarket("");
  }, [loading, error, market, selectedMarket]);
  const changeCommodity = (value: string) => {
    setCommodity(value);
    // Match saved IDs, not names: different records can share the same label.
    if (value && market && !prices.some((item) => identityValue(item.commodity_id) === value && identityValue(item.market_id) === market)) setMarket("");
  };
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (loading || error) return;
    const query = new URLSearchParams();
    addIdentityFilter(query, "commodity", commodity);
    addIdentityFilter(query, "market", selectedMarket);
    navigate(`/prices${query.size ? `?${query}` : ""}#price-search`);
  };

  return <form className="home-price-search" role="search" aria-label="Search current prices" onSubmit={submit}>
    <h2>Find prices</h2>
    <fieldset disabled={loading || error} className="home-price-search-fields">
      <label>Commodity<select value={commodity} onChange={(event) => changeCommodity(event.target.value)}>
        <option value="">Choose a commodity</option>
        {commodities.map((item) => <option key={item.id} value={identityValue(item.id)}>{item.name}</option>)}
      </select></label>
      <label>Market<select value={selectedMarket} onChange={(event) => setMarket(event.target.value)}>
        <option value="">Choose a market</option>
        {availableMarkets.map((item) => <option key={item.id} value={identityValue(item.id)}>{item.name}</option>)}
      </select>{commodity && !loading && !error && !availableMarkets.length && <small>No registered markets for this commodity yet.</small>}</label>
      <button type="submit" className="button" disabled={loading || error}>Search prices</button>
    </fieldset>
    {loading && !error && <p className="home-search-status" role="status">Loading search options…</p>}
    {error && <p className="home-search-status" role="status">Search options could not be loaded. <Link className="text-link" to="/prices#price-search">Open current prices</Link> to try there.</p>}
  </form>;
}
