import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../services/api";
import { InstallPrompt } from "./InstallPrompt";
import { ButtonSpinner } from "./LoadingSpinner";
import { OfflineBanner } from "./OfflineBanner";
import { OnboardingTour } from "./OnboardingTour";
import { PriceTicker } from "./PriceTicker";
import { usePreferences } from "../context/PreferencesContext";
import { useToast } from "../context/ToastContext";
import { SUPPORT_WHATSAPP_NUMBER, WhatsAppSupportButton } from "./WhatsAppSupportButton";
import type { PriceUpdate } from "../types/api";
import { daysUntil, WHATSAPP_COMMUNITY_URL } from "../utils";

const VISIT_PING_KEY = "py_visit_pinged";
const TICKER_REFRESH_MS = 60_000;
// Admin needs focus for data entry, and Login/Register are deliberately minimal --
// everywhere else a trader is actually browsing gets the live ticker.
const TICKER_HIDDEN_PREFIXES = ["/admin", "/login", "/register"];

const navItems = [
  ["/prices", "Current Prices"],
  ["/history", "Price History"],
  ["/market-days", "Market Days"],
  ["/faq", "FAQ"],
] as const;

export function Layout() {
  const { user, accessLabel, subscription, logout, loading: authLoading } = useAuth();
  const trialDaysLeft = accessLabel === "Trial" ? daysUntil(subscription?.trial_ends_at) : null;
  const { dataSaver, toggleDataSaver, easyReading, toggleEasyReading, darkMode, toggleDarkMode } = usePreferences();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);
  const [tickerPrices, setTickerPrices] = useState<PriceUpdate[]>([]);
  const showTicker = !TICKER_HIDDEN_PREFIXES.some((prefix) => location.pathname.startsWith(prefix));

  useEffect(() => {
    if (!showTicker) return;
    const loadTicker = () => { void apiFetch<PriceUpdate[]>("/price-updates").then(setTickerPrices).catch(() => {}); };
    loadTicker();
    if (dataSaver) return;
    const interval = setInterval(loadTicker, TICKER_REFRESH_MS);
    return () => clearInterval(interval);
  }, [dataSaver, showTicker]);

  useEffect(() => {
    // Wait for auth to resolve so an already-logged-in admin's own visits never get
    // counted -- the activity feed exists to show the admin that OTHER people are
    // using the app, not to notify them about their own browsing.
    if (authLoading || user?.role === "admin") return;
    try {
      if (sessionStorage.getItem(VISIT_PING_KEY)) return;
      sessionStorage.setItem(VISIT_PING_KEY, "1");
    } catch {
      // storage unavailable (private mode, blocked) - ping anyway, just not deduped this session
    }
    void apiFetch("/activity/ping", { method: "POST", body: JSON.stringify({ event_type: "app_visit", label: location.pathname }) }).catch(() => {});
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [authLoading, user]);

  const handleLogout = async () => {
    if (loggingOut) return;
    setLoggingOut(true);
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    logout();
    setOpen(false);
    setLoggingOut(false);
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    showToast("Logout successful.");
    navigate("/", { replace: true });
  };

  return (
    <div className="app-shell">
      <header className="site-header">
        <div className="header-inner">
          <Link to="/" className="brand" onClick={() => setOpen(false)}>
            <span className="brand-mark">PY</span>
            <span><strong>PriceYard</strong><small>Know the market before you buy or sell.</small></span>
          </Link>
          <button className="menu-button" type="button" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen((value) => !value)}>☰ Menu</button>
          <nav className={open ? "main-nav open" : "main-nav"} aria-label="Primary navigation">
            <div className="nav-primary">
              {navItems.map(([to, label]) => <NavLink key={to} to={to} onClick={() => setOpen(false)}>{label}</NavLink>)}
            </div>
            <div className="nav-account">
              {user && <NavLink to="/watchlist" onClick={() => setOpen(false)}>Watchlist</NavLink>}
              {user && <NavLink to="/feedback" onClick={() => setOpen(false)}>Feedback</NavLink>}
              {user?.role === "admin" && <NavLink to="/admin" onClick={() => setOpen(false)}>Admin</NavLink>}
              {user ? (
                <>
                  <NavLink to="/dashboard" onClick={() => setOpen(false)}>Dashboard</NavLink>
                  <button className="nav-button" type="button" disabled={loggingOut} onClick={() => void handleLogout()}>{loggingOut ? <ButtonSpinner label="Please wait…" /> : "Log out"}</button>
                </>
              ) : (
                <NavLink className="nav-cta" to="/login" onClick={() => setOpen(false)}>Log in</NavLink>
              )}
            </div>
          </nav>
        </div>
        <div className="access-strip">
          <span>Access: <strong>{accessLabel}</strong></span>{user && <span>{user.full_name}</span>}
          <span className="display-toggles">
            <button type="button" className={dataSaver ? "toggle-pill on" : "toggle-pill"} aria-pressed={dataSaver} onClick={toggleDataSaver}>Data saver: {dataSaver ? "On" : "Off"}</button>
            <button type="button" className={easyReading ? "toggle-pill on" : "toggle-pill"} aria-pressed={easyReading} onClick={toggleEasyReading}>Easy reading: {easyReading ? "On" : "Off"}</button>
            <button type="button" className={darkMode ? "toggle-pill on" : "toggle-pill"} aria-pressed={darkMode} onClick={toggleDarkMode}>Dark mode: {darkMode ? "On" : "Off"}</button>
          </span>
        </div>
        {showTicker && <PriceTicker items={tickerPrices} />}
      </header>
      {trialDaysLeft !== null && trialDaysLeft >= 0 && (
        <div className="trial-banner">
          {trialDaysLeft === 0 ? "Your trial ends today." : <>Your trial ends in <strong>{trialDaysLeft} day{trialDaysLeft === 1 ? "" : "s"}</strong>.</>}
        </div>
      )}
      <OfflineBanner />
      <InstallPrompt />
      <main><Outlet /></main>
      {location.pathname !== "/" && (
        <div className="back-to-app"><Link className="text-link" to="/prices">← Back to Current Prices</Link></div>
      )}
      <footer className="site-footer">
        <div><strong>PriceYard</strong> by NGU TOP PRODUCTS AND SERVICES</div>
        <div>Market information only — no guaranteed profit or prediction.</div>
        <a className="text-link" href={WHATSAPP_COMMUNITY_URL} target="_blank" rel="noopener noreferrer">Join our free WhatsApp updates →</a>
        <a className="text-link" href={`https://wa.me/${SUPPORT_WHATSAPP_NUMBER}?text=${encodeURIComponent("Hi PriceYard, I'm interested in exploring a partnership.")}`} target="_blank" rel="noopener noreferrer">Partner with us →</a>
      </footer>
      <WhatsAppSupportButton />
      <OnboardingTour />
    </div>
  );
}
