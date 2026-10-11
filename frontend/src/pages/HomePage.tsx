import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { CommodityImage } from "../components/CommodityImage";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { PriceCard } from "../components/PriceCard";
import { NativeShareButton } from "../components/ShareButtons";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { usePreferences } from "../context/PreferencesContext";
import { apiFetch } from "../services/api";
import { useTranslation } from "../translations";
import type { Commodity, Market, PriceUpdate, Testimonial } from "../types/api";
import { comingSoonShareContent, comingSoonShareUrl, dateOnly, money, priceShareContent, relativeTime, whatsAppShareUrl, WHATSAPP_COMMUNITY_URL } from "../utils";

const AUTO_REFRESH_MS = 60_000;

export function HomePage() {
  useDocumentTitle("Know the market before you buy or sell");
  const { dataSaver } = usePreferences();
  const t = useTranslation();
  const [prices, setPrices] = useState<PriceUpdate[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [upcoming, setUpcoming] = useState<Commodity[]>([]);
  const [commodityCount, setCommodityCount] = useState<number | null>(null);
  const [marketCount, setMarketCount] = useState<number | null>(null);
  const [recordCount, setRecordCount] = useState<number | null>(null);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);

  const loadPrices = (silent = false) => {
    apiFetch<PriceUpdate[]>("/price-updates")
      .then((items) => { setPrices(items.slice(0, 3)); setRecordCount(items.length); })
      .catch((err: Error) => { if (!silent) setError(err.message); })
      .finally(() => { if (!silent) setLoading(false); });
  };

  useEffect(() => {
    loadPrices();
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
          <span className="eyebrow">{t("home_eyebrow")}</span>
          <h1>{t("home_headline")}</h1>
          <p>{t("home_subtext")}</p>
          {!loading && prices[0] && (
            <div className="hero-price-preview">
              <span className="eyebrow">{t("home_live_now")}</span>
              <p className="price-range">{prices[0].commodity.name}: {money(prices[0].price_low)} – {money(prices[0].price_high)}</p>
              <span className="muted">{prices[0].market.name} · updated {relativeTime(prices[0].update_date_time)}</span>
              <a className="text-link" href={whatsAppShareUrl(prices[0])} target="_blank" rel="noopener noreferrer">Share on WhatsApp →</a>
              <NativeShareButton content={priceShareContent(prices[0])} />
            </div>
          )}
          <div className="button-row">
            <Link className="button" to="/prices">{t("home_check_prices")}</Link>
            <Link className="button button-secondary" to="/market-days">{t("home_see_market_days")}</Link>
          </div>
        </div>
        <div className="hero-panel">
          <strong>{t("home_panel_title")}</strong>
          <ul>
            <li>{t("home_panel_li1")}</li>
            <li>{t("home_panel_li2")}</li>
            <li>{t("home_panel_li3")}</li>
            <li>{t("home_panel_li4")}</li>
          </ul>
          <a className="text-link" href={WHATSAPP_COMMUNITY_URL} target="_blank" rel="noopener noreferrer">{t("home_join_whatsapp")}</a>
        </div>
      </section>

      {commodityCount !== null && marketCount !== null && recordCount !== null && (
        <div className="page stats-strip">
          <span><strong>{commodityCount}</strong> {t("home_products_tracked")}</span>
          <span><strong>{marketCount}</strong> {t("home_markets_covered")}</span>
          <span><strong>{recordCount}</strong> {t("home_confirmed_prices")}</span>
        </div>
      )}

      {upcoming.length > 0 && (
        <section className="page section-block">
          <div className="section-heading"><div><span className="eyebrow">{t("home_coming_soon_eyebrow")}</span><h2>{t("home_coming_soon_heading")}</h2></div></div>
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
        <div className="section-heading"><div><span className="eyebrow">{t("home_today_eyebrow")}</span><h2>{t("home_today_heading")}</h2></div><Link className="text-link" to="/prices">{t("home_see_all_prices")}</Link></div>
        {loading ? <LoadingSpinner label="Loading approved prices…" /> : error ? <div className="status-box error">Could not load prices: {error}</div> : prices.length ? <div className="card-grid">{prices.map((item) => <PriceCard key={item.id} item={item} />)}</div> : <div className="status-box">No approved current price updates are available yet. Check back soon.</div>}
      </section>

      {testimonials.length > 0 && (
        <section className="page section-block">
          <div className="section-heading"><div><span className="eyebrow">{t("home_testimonials_eyebrow")}</span><h2>{t("home_testimonials_heading")}</h2></div></div>
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
        <article className="info-tile"><span>01</span><h3>{t("home_tile1_title")}</h3><p>{t("home_tile1_body")}</p></article>
        <article className="info-tile"><span>02</span><h3>{t("home_tile2_title")}</h3><p>{t("home_tile2_body")}</p></article>
        <article className="info-tile"><span>03</span><h3>{t("home_tile3_title")}</h3><p>{t("home_tile3_body")}</p></article>
      </section>

      <section className="page section-block"><Disclaimer>{PRICE_DISCLAIMER}</Disclaimer></section>
    </>
  );
}
