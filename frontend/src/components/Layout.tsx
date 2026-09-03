import { useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { ButtonSpinner } from "./LoadingSpinner";
import { useToast } from "../context/ToastContext";
import "./MobileHeaderNav.css";

const navItems = [
  ["/prices", "Prices", "prices"],
  ["/history", "History", "history"],
  ["/market-days", "Market Days", "calendar"],
  ["/faq", "FAQ", "faq"],
] as const;

type NavIconName = "prices" | "history" | "calendar" | "faq" | "watchlist" | "feedback" | "admin" | "dashboard" | "login" | "logout";

function NavIcon({ name }: { name: NavIconName }) {
  const common = {
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.9,
    strokeLinecap: "round" as const,
    strokeLinejoin: "round" as const,
    "aria-hidden": true,
  };

  switch (name) {
    case "prices":
      return <span className="mobile-nav-icon"><svg {...common}><path d="M4 18V9"/><path d="M10 18V5"/><path d="M16 18v-7"/><path d="M3 18h18"/><path d="m15 7 2-2 2 2"/></svg></span>;
    case "history":
      return <span className="mobile-nav-icon"><svg {...common}><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 7v5l3 2"/></svg></span>;
    case "calendar":
      return <span className="mobile-nav-icon"><svg {...common}><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/><path d="M8 14h2M14 14h2M8 17h2"/></svg></span>;
    case "faq":
      return <span className="mobile-nav-icon"><svg {...common}><circle cx="12" cy="12" r="9"/><path d="M9.8 9a2.4 2.4 0 0 1 4.6 1c0 1.8-2.4 2-2.4 3.5"/><path d="M12 17h.01"/></svg></span>;
    case "watchlist":
      return <span className="mobile-nav-icon"><svg {...common}><path d="m12 3 2.8 5.7 6.2.9-4.5 4.4 1.1 6.2-5.6-3-5.6 3 1.1-6.2L3 9.6l6.2-.9L12 3Z"/></svg></span>;
    case "feedback":
      return <span className="mobile-nav-icon"><svg {...common}><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4v8Z"/><path d="M8 9h8M8 13h5"/></svg></span>;
    case "admin":
      return <span className="mobile-nav-icon"><svg {...common}><path d="M12 3 4 6v5c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V6l-8-3Z"/><path d="M9.5 12.2 11 14l3.8-4"/></svg></span>;
    case "dashboard":
      return <span className="mobile-nav-icon"><svg {...common}><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg></span>;
    case "logout":
      return <span className="mobile-nav-icon"><svg {...common}><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/><path d="M14 3h4a3 3 0 0 1 3 3v12a3 3 0 0 1-3 3h-4"/></svg></span>;
    case "login":
    default:
      return <span className="mobile-nav-icon"><svg {...common}><path d="m14 7 5 5-5 5"/><path d="M19 12H7"/><path d="M10 3H6a3 3 0 0 0-3 3v12a3 3 0 0 0 3 3h4"/></svg></span>;
  }
}

function NavText({ children }: { children: string }) {
  return <span className="nav-label">{children}</span>;
}

export function Layout() {
  const { user, accessLabel, logout } = useAuth();
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
          <Link to="/" className="brand" onClick={() => setOpen(false)} aria-label="PriceYard home">
            <span className="brand-mark">PY</span>
            <span><strong>PriceYard</strong><small>Know the market before you buy or sell.</small></span>
          </Link>
          <button className="menu-button" type="button" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen((value) => !value)}>Menu</button>
          <nav className={open ? "main-nav open" : "main-nav"} aria-label="Primary navigation">
            {navItems.map(([to, label, icon]) => (
              <NavLink key={to} to={to} onClick={() => setOpen(false)} aria-label={label} title={label}>
                <NavIcon name={icon} /><NavText>{label}</NavText>
              </NavLink>
            ))}
            {user && <NavLink to="/watchlist" onClick={() => setOpen(false)} aria-label="Watchlist" title="Watchlist"><NavIcon name="watchlist"/><NavText>Watchlist</NavText></NavLink>}
            {user && <NavLink to="/feedback" onClick={() => setOpen(false)} aria-label="Feedback" title="Feedback"><NavIcon name="feedback"/><NavText>Feedback</NavText></NavLink>}
            {user?.role === "admin" && <NavLink to="/admin" onClick={() => setOpen(false)} aria-label="Admin" title="Admin"><NavIcon name="admin"/><NavText>Admin</NavText></NavLink>}
            {user ? (
              <>
                <NavLink to="/dashboard" onClick={() => setOpen(false)} aria-label="Dashboard" title="Dashboard"><NavIcon name="dashboard"/><NavText>Dashboard</NavText></NavLink>
                <button className="nav-button" type="button" disabled={loggingOut} onClick={() => void handleLogout()} aria-label="Log out" title="Log out">{loggingOut ? <ButtonSpinner label="Please wait…" /> : <><NavIcon name="logout"/><NavText>Log out</NavText></>}</button>
              </>
            ) : (
              <NavLink className="nav-cta" to="/login" onClick={() => setOpen(false)} aria-label="Log in" title="Log in"><NavIcon name="login"/><NavText>Log in</NavText></NavLink>
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
