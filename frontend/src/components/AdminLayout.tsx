import { NavLink, Outlet } from "react-router-dom";

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
  return <section className="page page-section admin-page">
    <div className="page-title"><span className="eyebrow">Administrator</span><h1>PriceYard admin</h1><p>Manage the approved MVP records without changing the product scope.</p></div>
    <nav className="admin-nav" aria-label="Admin navigation">
      {adminLinks.map(([to, label]) => <NavLink key={to} to={to} end={to === "/admin"}>{label}</NavLink>)}
    </nav>
    <div className="admin-content"><Outlet /></div>
  </section>;
}
