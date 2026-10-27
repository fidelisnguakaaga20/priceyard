import { relativePriceTime } from "../utils/priceTime";
import { useEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { HomePriceSearch } from "../components/HomePriceSearch";
import { GroupedPriceCards } from "../components/GroupedPriceCards";
import { SavedPriceNotice } from "../components/SavedPriceNotice";
import { NativeShareButton } from "../components/ShareButtons";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { usePreferences } from "../context/PreferencesContext";
import { apiFetch, apiFetchWithProvenance } from "../services/api";
import type { Commodity, Market, PriceUpdate, Testimonial } from "../types/api";
import { comingSoonShareContent, comingSoonShareUrl, dateOnly, money, priceShareContent, whatsAppShareUrl, WHATSAPP_COMMUNITY_URL } from "../utils";

const AUTO_REFRESH_MS = 60_000;

export function HomePage() {
  useDocumentTitle("Know the market before you buy or sell");
  const { dataSaver } = usePreferences();
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const priceRequest = useRef(0);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [upcoming, setUpcoming] = useState<Commodity[]>([]);
  const [searchCommodities, setSearchCommodities] = useState<Commodity[]>([]);
  const [searchMarkets, setSearchMarkets] = useState<Market[]>([]);
  const [searchCatalogsPending, setSearchCatalogsPending] = useState(2);
  const [searchCatalogError, setSearchCatalogError] = useState(false);
  const [commodityCount, setCommodityCount] = useState<number | null>(null);
  const [marketCount, setMarketCount] = useState<number | null>(null);
  const [recordCount, setRecordCount] = useState<number | null>(null);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);

  const loadPrices = (silent = false) => {
    const sequence = ++priceRequest.current;
    apiFetchWithProvenance<PriceUpdate[]>("/price-updates")
      .then(({ data: items, savedAt }) => { if (sequence !== priceRequest.current) return; setPrices(items); setSavedAt(savedAt); setRecordCount(items.length); setError(""); })
      .catch((err: Error) => { if (sequence === priceRequest.current && !silent) setError(err.message); })
      .finally(() => { if (sequence === priceRequest.current && !silent) setLoading(false); });
  };

  useEffect(() => {
    let current = true;
    loadPrices();
    apiFetch<Commodity[]>("/commodities")
      .then((items) => {
        if (!current) return;
        setUpcoming(items.filter((item) => item.is_upcoming));
        const tracked = items.filter((item) => !item.is_upcoming);
        setSearchCommodities(tracked);
        setCommodityCount(tracked.length);
      })
      .catch(() => { if (current) setSearchCatalogError(true); })
      .finally(() => { if (current) setSearchCatalogsPending((pending) => pending - 1); });
    apiFetch<Market[]>("/markets")
      .then((items) => { if (current) { setSearchMarkets(items); setMarketCount(items.length); } })
      .catch(() => { if (current) setSearchCatalogError(true); })
      .finally(() => { if (current) setSearchCatalogsPending((pending) => pending - 1); });
    apiFetch<Testimonial[]>("/testimonials")
      .then(setTestimonials)
      .catch(() => undefined);
    return () => { current = false; priceRequest.current++; };
  }, []);

  // Silently keep the homepage's prices current while it's open (ticker + "Today's
  // prices"), skipped under Data saver since it costs mobile data on a page people
  // often leave open.
  useEffect(() => {
    if (dataSaver) return;
    const interval = setInterval(() => loadPrices(true), AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [dataSaver]);

  return (
    <>
      <section className="hero page">
        <div className="hero-copy">
          <span className="eyebrow">Market price information</span>
          <h1>Know the market before you buy or sell.</h1>
          <p>See today's and past prices, price changes, and real market updates for Egusi, Honey Beans and Palm oil.</p>
          <HomePriceSearch commodities={searchCommodities} markets={searchMarkets}
            loading={searchCatalogsPending > 0} error={searchCatalogError} />
          {!loading && prices[0] && (
            <div className="hero-price-preview">
              {!savedAt && <span className="eyebrow">Live now</span>}
              <SavedPriceNotice savedAt={savedAt} />
              <p className="price-range">{prices[0].commodity.name}: {money(prices[0].price_low)} – {money(prices[0].price_high)}</p>
              <span className="muted">{prices[0].market.name} · updated {relativePriceTime(prices[0].update_date_time)}</span>
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
                <a className="text-link" href={comingSoonShareUrl(item)} target="_blank" rel="noopener noreferrer">Tell a friend on WhatsApp →</a>
                <NativeShareButton content={comingSoonShareContent(item)} />
              </article>
            ))}
          </div>
        </section>
      )}

      <section className="page section-block">
        <div className="section-heading"><div><span className="eyebrow">Latest market information</span><h2>Today's prices</h2></div><Link className="text-link" to="/prices">See all prices →</Link></div>
        {!loading && prices.length > 0 && <SavedPriceNotice savedAt={savedAt} />}
        {loading ? <LoadingSpinner label="Loading approved prices…" /> : error ? <div className="status-box error">Could not load prices: {error}</div> : prices.length ? <GroupedPriceCards items={prices} /> : <div className="status-box">No approved current price updates are available yet. Check back soon.</div>}
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
