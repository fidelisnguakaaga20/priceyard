import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import type { Commodity, Market, PriceUpdate, Subscription, User } from "../../types/api";
import { AdminLoading, errorText } from "./adminUtils";

type Summary = { count: number; average_rating: number | null };
type Metrics = { users: number; commodities: number; markets: number; latest: number; outdated: number; trial: number; active: number; feedback: number; average: number | null };

export function AdminDashboardPage() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => { if (!token) return; void (async () => {
    try {
      const [users, commodities, markets, latest, history, subscriptions, feedback] = await Promise.all([
        apiFetch<User[]>("/users", {}, token), apiFetch<Commodity[]>("/commodities", {}, token), apiFetch<Market[]>("/markets", {}, token),
        apiFetch<PriceUpdate[]>("/price-updates", {}, token), apiFetch<PriceUpdate[]>("/price-updates/history", {}, token),
        apiFetch<Subscription[]>("/subscriptions", {}, token), apiFetch<Summary>("/feedback/summary", {}, token),
      ]);
      setMetrics({ users: users.length, commodities: commodities.length, markets: markets.length, latest: latest.length,
        outdated: history.filter((item) => item.is_outdated).length, trial: subscriptions.filter((item) => item.status === "trial").length,
        active: users.filter((item) => item.is_active).length, feedback: feedback.count, average: feedback.average_rating });
    } catch (err) { setError(errorText(err)); }
    finally { setLoading(false); }
  })(); }, [token]);
  const cards = metrics ? [
    ["Total users", metrics.users], ["Commodities", metrics.commodities], ["Markets", metrics.markets], ["Latest updates", metrics.latest],
    ["Outdated prices", metrics.outdated], ["Trial users", metrics.trial], ["Active users", metrics.active], ["Feedback count", metrics.feedback],
    ["Average rating", metrics.average == null ? "—" : metrics.average.toFixed(2)],
  ] : [];
  return <div><div className="section-heading"><div><span className="eyebrow">Useful basics only</span><h2>Admin dashboard</h2></div></div>
    {error && <div className="status-box error">{error}</div>}
    {loading && <AdminLoading label="Loading dashboard…" />}
    <div className="admin-metric-grid">{cards.map(([label, value]) => <article className="admin-metric" key={label}><span>{label}</span><strong>{value}</strong></article>)}</div>
  </div>;
}
