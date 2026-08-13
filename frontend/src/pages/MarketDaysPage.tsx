import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
import type { Market } from "../types/api";

export function MarketDaysPage() {
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  useEffect(() => { apiFetch<Market[]>("/markets").then(setMarkets).catch((err: Error) => setError(err.message)); }, []);
  return <section className="page page-section"><div className="page-title"><span className="eyebrow">Market-day calendar</span><h1>Known market days</h1><p>Only market days already verified in PriceYard are shown as confirmed.</p></div>{error ? <div className="status-box error">{error}</div> : <div className="market-day-grid">{markets.filter((x) => x.is_active).map((market) => <article className="card" key={market.id}><span className="eyebrow">{market.state || "Nigeria"}</span><h2>{market.name}</h2><p className="market-day-value">{market.market_day || "Not yet verified"}</p>{market.description && <p className="muted">{market.description}</p>}</article>)}</div>}</section>;
}
