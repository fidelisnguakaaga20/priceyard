import { FormEvent, useEffect, useRef, useState } from "react";
import { useLocation, useSearchParams } from "react-router-dom";
import { Disclaimer, PRICE_DISCLAIMER } from "../components/Disclaimer";
import { ButtonSpinner, LoadingSpinner } from "../components/LoadingSpinner";
import { GroupedPriceCards } from "../components/GroupedPriceCards";
import { ONBOARDING_TOUR_SEEN_EVENT } from "../components/OnboardingTour";
import { SavedPriceNotice } from "../components/SavedPriceNotice";
import { useCommodityMarketPairs } from "../hooks/useCommodityMarketPairs";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { usePreferences } from "../context/PreferencesContext";
import { apiFetch, apiFetchWithProvenance } from "../services/api";
import { addIdentityFilter, identityLabel, identityValue, selectedIdentity, selectionFromQuery } from "../services/priceIdentity";
import type { Commodity, Market, PriceUpdate } from "../types/api";

const AUTO_REFRESH_MS = 60_000;
type PriceFilters = { commodity?: string; market?: string; movement?: string };

export function PricesPage() {
  const { dataSaver } = usePreferences();
  useDocumentTitle("Current Prices");
  const location = useLocation();
  const [searchParams] = useSearchParams();
  const searchFormRef = useRef<HTMLFormElement>(null);
  const searchFocusKey = useRef<string | null>(null);
  const [items, setItems] = useState<PriceUpdate[]>([]);
  const [savedAt, setSavedAt] = useState<string | null>(null);
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [markets, setMarkets] = useState<Market[]>([]);
  const [commodity, setCommodity] = useState(() => selectionFromQuery(searchParams, "commodity"));
  const [market, setMarket] = useState(() => selectionFromQuery(searchParams, "market"));
  const commodityMarketPairs = useCommodityMarketPairs();
  const commodityLabel = identityLabel(commodity, commodities);
  const marketLabel = identityLabel(market, markets);
  const trackedMarkets = commodityLabel && commodityMarketPairs.has(commodityLabel)
    ? markets.filter((item) => commodityMarketPairs.get(commodityLabel)!.has(item.name))
    : markets;
  const selectedMarket = markets.find((item) => identityValue(item.id) === selectedIdentity(market, markets));
  // Preserve an explicit homepage/URL selection even if this pair has no prices.
  // The empty result should be clear, without silently changing the filter.
  const availableMarkets = selectedMarket && !trackedMarkets.some((item) => item.id === selectedMarket.id)
    ? [...trackedMarkets, selectedMarket] : trackedMarkets;
  const [movement, setMovement] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [filtersLoading, setFiltersLoading] = useState(true);
  const requestSequence = useRef(0);
  const foregroundPending = useRef(false);
  const appliedFilters = useRef<PriceFilters>({ commodity, market });

  const load = async (params?: PriceFilters, silent = false) => {
    if (silent && foregroundPending.current) return;
    const sequence = ++requestSequence.current;
    if (!silent) {
      foregroundPending.current = true;
      appliedFilters.current = params || {};
      setLoading(true); setError("");
    }
    const query = new URLSearchParams();
    addIdentityFilter(query, "commodity", params?.commodity);
    addIdentityFilter(query, "market", params?.market);
    if (params?.movement) query.set("movement", params.movement);
    try {
      const { data, savedAt } = await apiFetchWithProvenance<PriceUpdate[]>(`/price-updates${query.size ? `?${query}` : ""}`);
      if (sequence !== requestSequence.current) return;
      setItems(data);
      setSavedAt(savedAt);
      setError("");
    } catch (err) {
      if (sequence === requestSequence.current && !silent) setError((err as Error).message);
    } finally {
      if (sequence === requestSequence.current && !silent) {
        foregroundPending.current = false;
        setLoading(false);
      }
    }
  };

  useEffect(() => {
    const commodity = selectionFromQuery(searchParams, "commodity");
    const market = selectionFromQuery(searchParams, "market");
    setCommodity(commodity); setMarket(market); setMovement("");
    void load({ commodity, market });
    return () => { requestSequence.current++; foregroundPending.current = false; };
  }, [searchParams]);

  useEffect(() => {
    let current = true;
    void Promise.all([
      apiFetch<Commodity[]>("/commodities"),
      apiFetch<Market[]>("/markets"),
    ]).then(([commodityItems, marketItems]) => {
      if (!current) return;
      setCommodities(commodityItems);
      setMarkets(marketItems);
    }).catch(() => undefined).finally(() => { if (current) setFiltersLoading(false); });
    return () => { current = false; };
  }, []);

  // Silently keep the list current while it's open, so an admin's new/edited price
  // shows up without the user needing to reload -- skipped under Data saver, since
  // repeated background fetches cost mobile data that toggle exists to avoid.
  useEffect(() => {
    if (dataSaver) return;
    const interval = setInterval(() => { void load(appliedFilters.current, true); }, AUTO_REFRESH_MS);
    return () => clearInterval(interval);
  }, [dataSaver]);

  useEffect(() => {
    if (location.hash !== "#price-search" || loading || filtersLoading || searchFocusKey.current === location.key) return;
    let frame = 0;
    const reveal = () => {
      window.cancelAnimationFrame(frame);
      frame = window.requestAnimationFrame(() => {
        // A first-time visitor must finish the welcome before focus moves to search.
        if (document.querySelector(".onboarding-overlay") || searchFocusKey.current === location.key) return;
        const form = searchFormRef.current;
        if (!form) return;
        searchFocusKey.current = location.key;
        form.querySelector<HTMLSelectElement>("select")?.focus({ preventScroll: true });
        const header = document.querySelector(".site-header");
        const headerHeight = header ? header.getBoundingClientRect().height + (parseFloat(getComputedStyle(header).top) || 0) : 0;
        window.scrollTo({ top: Math.max(0, window.scrollY + form.getBoundingClientRect().top - headerHeight - 12), behavior: "auto" });
      });
    };
    reveal();
    window.addEventListener(ONBOARDING_TOUR_SEEN_EVENT, reveal);
    return () => {
      window.cancelAnimationFrame(frame);
      window.removeEventListener(ONBOARDING_TOUR_SEEN_EVENT, reveal);
    };
  }, [location.hash, location.key, loading, filtersLoading]);

  const submit = (event: FormEvent) => { event.preventDefault(); void load({ commodity: selectedIdentity(commodity, commodities), market: selectedIdentity(market, markets), movement }); };
  const clear = () => { setCommodity(""); setMarket(""); setMovement(""); void load(); };
  const changeCommodity = (value: string) => {
    setCommodity(value);
    const label = identityLabel(value, commodities);
    if (market && label && commodityMarketPairs.has(label) && !commodityMarketPairs.get(label)!.has(marketLabel)) setMarket("");
  };

  return <section className="page page-section">
    <div className="page-title"><span className="eyebrow">Latest approved records</span><h1>Prices</h1><p>Search current commodity price ranges by commodity, market and movement.</p></div>
    <form id="price-search" ref={searchFormRef} className="filter-bar" role="search" aria-label="Search current prices" onSubmit={submit}>
      <label>Commodity<select value={selectedIdentity(commodity, commodities)} onChange={(e) => changeCommodity(e.target.value)}><option value="">Choose a commodity</option>{commodities.map((item) => <option value={identityValue(item.id)} key={item.id}>{item.name}</option>)}</select></label>
      <label>Market<select value={selectedIdentity(market, markets)} onChange={(e) => setMarket(e.target.value)}><option value="">Choose a market</option>{availableMarkets.map((item) => <option value={identityValue(item.id)} key={item.id}>{item.name}</option>)}</select>{commodity && trackedMarkets.length < markets.length && <small className="muted">{commodityLabel} is only tracked at {trackedMarkets.length} market{trackedMarkets.length === 1 ? "" : "s"} here.</small>}</label>
      <label>Movement<select value={movement} onChange={(e) => setMovement(e.target.value)}><option value="">Any movement</option><option value="up">Up</option><option value="down">Down</option><option value="stable">Stable</option><option value="unknown">Unknown</option></select></label>
      <div className="filter-actions"><button className="button button-small" type="submit" disabled={loading}>{loading ? <ButtonSpinner label="Please wait…" /> : "Apply"}</button><button className="button button-ghost button-small" type="button" onClick={clear} disabled={loading}>Clear</button></div>
    </form>
    {error && <div className="status-box error">{error}</div>}
    {!loading && items.length > 0 && <SavedPriceNotice savedAt={savedAt} />}
    {loading || filtersLoading ? <LoadingSpinner label="Loading approved prices…" /> : items.length ? <GroupedPriceCards items={items} /> : <div className="status-box">No current prices found{commodity ? ` for ${commodityLabel}` : ""}{market ? ` at ${marketLabel}` : ""}. Try clearing the filters or check back soon for new records.</div>}
    <Disclaimer>{PRICE_DISCLAIMER}</Disclaimer>
  </section>;
}
