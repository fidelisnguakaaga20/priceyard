import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { PriceCard } from "../components/PriceCard";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";

export function HomePage() {
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    apiFetch<PriceUpdate[]>("/price-updates")
      .then((items) => setPrices(items.slice(0, 3)))
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <>
      <section className="hero page">
        <div className="hero-copy">
          <span className="eyebrow">Agricultural market intelligence</span>
          <h1>Know the market before you buy or sell.</h1>
          <p>Track current and previous price ranges, market movement, confidence and practical market observations for Egusi, Beans and Palm oil.</p>
          <div className="button-row">
            <Link className="button" to="/prices">Check prices</Link>
            <Link className="button button-secondary" to="/market-days">View market days</Link>
          </div>
        </div>
        <div className="hero-panel">
          <strong>PriceYard starts focused.</strong>
          <ul>
            <li>Egusi, Beans, Palm oil</li>
            <li>Abuja/FCT, Kwali, Nasarawa, Benue</li>
            <li>Price ranges — not false precision</li>
            <li>Confidence labels and last updated time</li>
          </ul>
        </div>
      </section>

      <section className="page section-block">
        <div className="section-heading"><div><span className="eyebrow">Latest intelligence</span><h2>Current approved price updates</h2></div><Link className="text-link" to="/prices">See all prices →</Link></div>
        {error ? <div className="status-box error">Could not load prices: {error}</div> : prices.length ? <div className="card-grid">{prices.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No approved current price updates are available yet.</div>}
      </section>

      <section className="page section-block three-column">
        <article className="info-tile"><span>01</span><h3>Compare ranges</h3><p>See current and previous ranges without pretending every market transaction has one exact price.</p></article>
        <article className="info-tile"><span>02</span><h3>Read the signal</h3><p>Possible Meaning and Suggested Action stay observational and are never presented as guaranteed trading instructions.</p></article>
        <article className="info-tile"><span>03</span><h3>Check confidence</h3><p>Use source confidence, market timing and freshness before making a major buying, selling or storage decision.</p></article>
      </section>

      <section className="page section-block"><Disclaimer>{PRICE_DISCLAIMER}</Disclaimer></section>
    </>
  );
}
