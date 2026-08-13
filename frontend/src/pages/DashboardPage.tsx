import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { dateOnly } from "../utils";

export function DashboardPage() {
  const { user, subscription, accessLabel, hasFullAccess } = useAuth();
  if (!user) return null;
  return <section className="page page-section"><div className="page-title"><span className="eyebrow">User dashboard</span><h1>Welcome, {user.full_name}</h1><p>Your account, access level and shortcuts to PriceYard tools.</p></div>
    <div className="dashboard-grid">
      <article className="card"><span className="eyebrow">Current access</span><h2>{accessLabel}</h2><p>{hasFullAccess ? "Full approved market-intelligence viewing is available." : "Limited viewing is active. Full intelligence requires an active trial or paid status."}</p>{subscription && <dl className="data-list compact"><div><dt>Status</dt><dd>{subscription.status}</dd></div><div><dt>Trial ends</dt><dd>{dateOnly(subscription.trial_ends_at)}</dd></div><div><dt>Plan</dt><dd>{subscription.plan_name}</dd></div></dl>}</article>
      <article className="card"><span className="eyebrow">Account</span><h2>{user.email}</h2><p>Role: {user.role.replace(/_/g, " ")}</p><p className="muted">PriceYard backend authorization remains the authority for protected actions.</p></article>
    </div>
    <div className="shortcut-grid"><Link className="shortcut" to="/prices"><strong>Prices</strong><span>Check current approved ranges →</span></Link><Link className="shortcut" to="/watchlist"><strong>Watchlist</strong><span>Review saved commodities and markets →</span></Link><Link className="shortcut" to="/feedback"><strong>Feedback</strong><span>Rate PriceYard and suggest improvements →</span></Link><Link className="shortcut" to="/history"><strong>History</strong><span>Review chronological price records →</span></Link>{user.role === "admin" && <Link className="shortcut" to="/admin"><strong>Admin</strong><span>Manage PriceYard MVP records →</span></Link>}</div>
  </section>;
}
