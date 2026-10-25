import { useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { addIdentityFilter, identityValue } from "../services/priceIdentity";
import type { Commodity, Market } from "../types/api";
import "./HomePriceSearch.css";

/** Reuses the homepage's public catalogues; results use the existing price filters. */
export function HomePriceSearch({ commodities, markets, loading, error }: {
  commodities: Commodity[]; markets: Market[]; loading: boolean; error: boolean;
}) {
  const navigate = useNavigate();
  const [commodity, setCommodity] = useState("");
  const [market, setMarket] = useState("");
  const submit = (event: FormEvent) => {
    event.preventDefault();
    if (loading || error) return;
    const query = new URLSearchParams();
    addIdentityFilter(query, "commodity", commodity);
    addIdentityFilter(query, "market", market);
    navigate(`/prices${query.size ? `?${query}` : ""}#price-search`);
  };

  return <form className="home-price-search" role="search" aria-label="Search current prices" onSubmit={submit}>
    <h2>Find prices</h2>
    <fieldset disabled={loading || error} className="home-price-search-fields">
      <label>Commodity<select value={commodity} onChange={(event) => setCommodity(event.target.value)}>
        <option value="">Any commodity</option>
        {commodities.map((item) => <option key={item.id} value={identityValue(item.id)}>{item.name}</option>)}
      </select></label>
      <label>Market<select value={market} onChange={(event) => setMarket(event.target.value)}>
        <option value="">Any market</option>
        {markets.map((item) => <option key={item.id} value={identityValue(item.id)}>{item.name}</option>)}
      </select></label>
      <button type="submit" className="button" disabled={loading || error}>Search prices</button>
    </fieldset>
    {loading && !error && <p className="home-search-status" role="status">Loading search options…</p>}
    {error && <p className="home-search-status" role="status">Search options could not be loaded. <Link className="text-link" to="/prices#price-search">Open current prices</Link> to try there.</p>}
  </form>;
}
