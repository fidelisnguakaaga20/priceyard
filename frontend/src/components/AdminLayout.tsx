import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";
import { apiFetch } from "../services/api";
import { useAuth } from "../context/AuthContext";
import type { ActivitySummary } from "../types/api";

const POLL_MS = 45_000;

const adminLinks = [
  ["/admin", "Overview"],
  ["/admin/users", "Users"],
  ["/admin/commodities", "Commodities"],
  ["/admin/markets", "Markets"],
  ["/admin/prices", "Price updates"],
  ["/admin/market-signals", "Market signals"],
  ["/admin/quality-signals", "Quality signals"],
  ["/admin/buying-zones", "Buying zones"],
  ["/admin/sell-watch", "Sell-watch"],
  ["/admin/storage", "Storage"],
  ["/admin/costs", "Costs"],
  ["/admin/faq", "FAQ"],
  ["/admin/subscriptions", "Subscriptions"],
  ["/admin/payments", "Payments"],
  ["/admin/feedback", "Feedback"],
  ["/admin/audit", "Audit logs"],
  ["/admin/export", "CSV export"],
] as const;

export function AdminLayout() {
  const { token } = useAuth();
  const [unseen, setUnseen] = useState(0);

  useEffect(() => {
    if (!token) return;
    let cancelled = false;
    const poll = () => { void apiFetch<ActivitySummary>("/activity/summary", {}, token).then((data) => { if (!cancelled) setUnseen(data.unseen_count); }).catch(() => {}); };
    poll();
    const interval = setInterval(poll, POLL_MS);
    return () => { cancelled = true; clearInterval(interval); };
  }, [token]);

  return <section className="page page-section admin-page">
    <div className="page-title"><span className="eyebrow">Administrator</span><h1>PriceYard admin</h1><p>Manage the approved MVP records without changing the product scope.</p></div>
    <nav className="admin-nav" aria-label="Admin navigation">
      {adminLinks.map(([to, label]) => <NavLink key={to} to={to} end={to === "/admin"}>{label}</NavLink>)}
      <NavLink to="/admin/activity" onClick={() => setUnseen(0)}>Activity{unseen > 0 && <span className="admin-nav-badge">{unseen}</span>}</NavLink>
    </nav>
    <div className="admin-content"><Outlet /></div>
  </section>;
}
