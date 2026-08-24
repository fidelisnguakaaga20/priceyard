import { useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ButtonSpinner } from "./LoadingSpinner";

const navItems = [
  ["/prices", "Prices"],
  ["/history", "History"],
  ["/market-days", "Market Days"],
  ["/faq", "FAQ"],
] as const;

export function Layout() {
  const { user, accessLabel, logout } = useAuth();
  const [open, setOpen] = useState(false);
  const [loggingOut, setLoggingOut] = useState(false);

  const handleLogout = async () => {
    if (loggingOut) return;
    setLoggingOut(true);
    await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
    logout();
    setOpen(false);
    setLoggingOut(false);
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
            {navItems.map(([to, label]) => <NavLink key={to} to={to} onClick={() => setOpen(false)}>{label}</NavLink>)}
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
          </nav>
        </div>
        <div className="access-strip"><span>Access: <strong>{accessLabel}</strong></span>{user && <span>{user.full_name}</span>}</div>
      </header>
      <main><Outlet /></main>
      <footer className="site-footer">
        <div><strong>PriceYard</strong> by NGU TOP PRODUCTS AND SERVICES</div>
        <div>Market information only — no guaranteed profit or prediction.</div>
      </footer>
    </div>
  );
}
