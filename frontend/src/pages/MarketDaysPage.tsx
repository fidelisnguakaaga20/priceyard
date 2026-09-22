import { useEffect, useState } from "react";
import { CommodityImage } from "../components/CommodityImage";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { Market } from "../types/api";

export function MarketDaysPage() {
  useDocumentTitle("Market Days");
  const [markets, setMarkets] = useState<Market[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => { apiFetch<Market[]>("/markets").then(setMarkets).catch((err: Error) => setError(err.message)).finally(() => setLoading(false)); }, []);
  return <section className="page page-section"><div className="page-title"><span className="eyebrow">Market-day calendar</span><h1>Known market days</h1><p>Only market days already verified in PriceYard are shown as confirmed.</p></div>{loading ? <LoadingSpinner label="Loading market days…" /> : error ? <div className="status-box error">{error}</div> : <div className="market-day-grid">{markets.filter((x) => x.is_active).map((market) => <article className="card" key={market.id}><CommodityImage src={market.image_url} alt={market.name} /><span className="eyebrow">{market.state || "Nigeria"}</span><h2>{market.name}</h2><p className="market-day-value">{market.market_day || (market.description ? "Rotating schedule" : "Not yet verified")}</p>{market.description && <p className="muted">{market.description}</p>}</article>)}</div>}</section>;
}
