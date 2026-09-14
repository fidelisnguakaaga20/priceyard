import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ButtonSpinner } from "./LoadingSpinner";
import { usePreferences } from "../context/PreferencesContext";
import { useToast } from "../context/ToastContext";
import { daysUntil } from "../utils";

const navItems = [
  ["/prices", "Current Prices"],
  ["/history", "Price History"],
  ["/market-days", "Market Days"],
  ["/faq", "FAQ"],
] as const;

export function Layout() {
  const { user, accessLabel, subscription, logout } = useAuth();
  const trialDaysLeft = accessLabel === "Trial" ? daysUntil(subscription?.trial_ends_at) : null;
  const { dataSaver, toggleDataSaver, easyReading, toggleEasyReading } = usePreferences();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

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
          <button className="menu-button" type="button" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen((value) => !value)}>Menu</button>
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
          </span>
        </div>
      </header>
      {trialDaysLeft !== null && trialDaysLeft >= 0 && (
        <div className="trial-banner">
          {trialDaysLeft === 0 ? "Your trial ends today." : <>Your trial ends in <strong>{trialDaysLeft} day{trialDaysLeft === 1 ? "" : "s"}</strong>.</>}
        </div>
      )}
      <main><Outlet /></main>
      <footer className="site-footer">
        <div><strong>PriceYard</strong> by NGU TOP PRODUCTS AND SERVICES</div>
        <div>Market information only — no guaranteed profit or prediction.</div>
      </footer>
    </div>
  );
}
