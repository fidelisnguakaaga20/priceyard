import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PriceCard } from "../components/PriceCard";
import { NativeShareButton } from "../components/ShareButtons";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { Commodity, Market, PriceUpdate, Testimonial } from "../types/api";
import { comingSoonShareContent, comingSoonShareUrl, dateOnly, money, priceShareContent, relativeTime, whatsAppShareUrl, WHATSAPP_COMMUNITY_URL } from "../utils";

export function HomePage() {
  useDocumentTitle("Know the market before you buy or sell");
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [upcoming, setUpcoming] = useState<Commodity[]>([]);
  const [commodityCount, setCommodityCount] = useState<number | null>(null);
  const [marketCount, setMarketCount] = useState<number | null>(null);
  const [recordCount, setRecordCount] = useState<number | null>(null);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);

  useEffect(() => {
    apiFetch<PriceUpdate[]>("/price-updates")
      .then((items) => { setPrices(items.slice(0, 3)); setRecordCount(items.length); })
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
    apiFetch<Commodity[]>("/commodities")
      .then((items) => {
        setUpcoming(items.filter((item) => item.is_upcoming));
        setCommodityCount(items.filter((item) => !item.is_upcoming).length);
      })
      .catch(() => undefined);
    apiFetch<Market[]>("/markets")
      .then((items) => setMarketCount(items.length))
      .catch(() => undefined);
    apiFetch<Testimonial[]>("/testimonials")
      .then(setTestimonials)
      .catch(() => undefined);
  }, []);

  return (
    <>
      <section className="hero page">
        <div className="hero-copy">
          <span className="eyebrow">Market price information</span>
          <h1>Know the market before you buy or sell.</h1>
          <p>See today's and past prices, price changes, and real market updates for Egusi, Honey Beans and Palm oil.</p>
          {!loading && prices[0] && (
            <div className="hero-price-preview">
              <span className="eyebrow">Live now</span>
              <p className="price-range">{prices[0].commodity.name}: {money(prices[0].price_low)} – {money(prices[0].price_high)}</p>
              <span className="muted">{prices[0].market.name} · updated {relativeTime(prices[0].update_date_time)}</span>
              <a className="text-link" href={whatsAppShareUrl(prices[0])} target="_blank" rel="noopener noreferrer">Share on WhatsApp →</a>
              <NativeShareButton content={priceShareContent(prices[0])} />
            </div>
          )}
          <div className="button-row">
            <Link className="button" to="/prices">Check prices</Link>
            <Link className="button button-secondary" to="/market-days">See market days</Link>
          </div>
        </div>
        <div className="hero-panel">
          <strong>PriceYard starts focused.</strong>
          <ul>
            <li>PriceYard covers Egusi, Honey Beans, Palm oil</li>
            <li>Abuja/FCT, Kwali, Nasarawa, Benue</li>
            <li>Real price range, not one fixed number</li>
            <li>How sure we are about the price, and when it was last checked</li>
          </ul>
          <a className="text-link" href={WHATSAPP_COMMUNITY_URL} target="_blank" rel="noopener noreferrer">Join our free WhatsApp updates →</a>
        </div>
      </section>

      {commodityCount !== null && marketCount !== null && recordCount !== null && (
        <div className="page stats-strip">
          <span><strong>{commodityCount}</strong> product{commodityCount === 1 ? "" : "s"} tracked</span>
          <span><strong>{marketCount}</strong> market{marketCount === 1 ? "" : "s"} covered</span>
          <span><strong>{recordCount}</strong> confirmed price{recordCount === 1 ? "" : "s"}</span>
        </div>
      )}

      {upcoming.length > 0 && (
        <section className="page section-block">
          <div className="section-heading"><div><span className="eyebrow">Coming soon</span><h2>New products coming soon</h2></div></div>
          <div className="card-grid">
            {upcoming.map((item) => (
              <article className="card" key={item.id}>
                <CommodityImage src={item.image_url} alt={item.name} />
                <span className="eyebrow">Coming soon</span>
                <h3>{item.name}</h3>
                {item.description && <p className="muted">{item.description}</p>}
                {item.expected_available_date && <p className="muted"><strong>Expected:</strong> {dateOnly(item.expected_available_date)}</p>}
                <a className="text-link" href={comingSoonShareUrl(item.name)} target="_blank" rel="noopener noreferrer">Tell a friend on WhatsApp →</a>
                <NativeShareButton content={comingSoonShareContent(item.name)} />
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="page section-block">
        <div className="section-heading"><div><span className="eyebrow">Latest market information</span><h2>Today's prices</h2></div><Link className="text-link" to="/prices">See all prices →</Link></div>
        {loading ? <LoadingSpinner label="Loading approved prices…" /> : error ? <div className="status-box error">Could not load prices: {error}</div> : prices.length ? <div className="card-grid">{prices.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No approved current price updates are available yet. Check back soon.</div>}
      </section>

      {testimonials.length > 0 && (
        <section className="page section-block">
          <div className="section-heading"><div><span className="eyebrow">From real users</span><h2>What traders are saying</h2></div></div>
          <div className="card-grid">
            {testimonials.map((item) => (
              <article className="card testimonial-card" key={item.id}>
                <span className="testimonial-stars" aria-label={`${item.rating} out of 5 stars`}>{"★".repeat(item.rating)}{"☆".repeat(5 - item.rating)}</span>
                <p>&ldquo;{item.quote}&rdquo;</p>
                <strong>— {item.display_name}</strong>
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="page section-block three-column">
        <article className="info-tile"><span>01</span><h3>Compare prices</h3><p>See current and previous ranges without pretending every market transaction has one exact price.</p></article>
        <article className="info-tile"><span>02</span><h3>Read our market notes</h3><p>Possible Meaning and Suggested Action stay observational and are never presented as guaranteed trading instructions.</p></article>
        <article className="info-tile"><span>03</span><h3>Check how sure we are</h3><p>Use source confidence, market timing and freshness before making a major buying, selling or storage decision.</p></article>
      </section>

      <section className="page section-block"><Disclaimer>{PRICE_DISCLAIMER}</Disclaimer></section>
    </>
  );
}
