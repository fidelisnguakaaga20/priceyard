import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import type { Commodity, Market, PriceUpdate, Subscription, User } from "../../types/api";
import { AdminLoading, errorText } from "./adminUtils";

type Summary = { count: number; average_rating: number | null };
type FeedbackRow = { is_public_testimonial: boolean };
type PaymentRow = { status: string; amount: string | number };
type Metrics = {
  users: number; commodities: number; markets: number; latest: number; outdated: number; trial: number; active: number; feedback: number; average: number | null;
  newUsersWeek: number; referralsUsed: number; testimonialsLive: number; successfulPayments: number; revenue: number;
};

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;

export function AdminDashboardPage() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => { if (!token) return; void (async () => {
    try {
      const [users, commodities, markets, latest, history, subscriptions, feedback, feedbackList, payments] = await Promise.all([
        apiFetch<User[]>("/users", {}, token), apiFetch<Commodity[]>("/commodities/admin/all", {}, token), apiFetch<Market[]>("/markets/admin/all", {}, token),
        apiFetch<PriceUpdate[]>("/price-updates", {}, token), apiFetch<PriceUpdate[]>("/price-updates/admin/history", {}, token),
        apiFetch<Subscription[]>("/subscriptions", {}, token), apiFetch<Summary>("/feedback/summary", {}, token),
        apiFetch<FeedbackRow[]>("/feedback", {}, token), apiFetch<PaymentRow[]>("/payments", {}, token),
      ]);
      const weekAgo = Date.now() - WEEK_MS;
      const successful = payments.filter((p) => p.status === "success");
      setMetrics({
        users: users.length, commodities: commodities.length, markets: markets.length, latest: latest.length,
        outdated: history.filter((item) => item.is_outdated).length, trial: subscriptions.filter((item) => item.status === "trial").length,
        active: users.filter((item) => item.is_active).length, feedback: feedback.count, average: feedback.average_rating,
        newUsersWeek: users.filter((u) => new Date(u.created_at).getTime() >= weekAgo).length,
        referralsUsed: users.filter((u) => u.referred_by_id !== null).length,
        testimonialsLive: feedbackList.filter((f) => f.is_public_testimonial).length,
        successfulPayments: successful.length,
        revenue: successful.reduce((sum, p) => sum + Number(p.amount), 0),
      });
    } catch (err) { setError(errorText(err)); }
    finally { setLoading(false); }
  })(); }, [token]);
  const cards = metrics ? [
    ["Total users", metrics.users], ["Commodities", metrics.commodities], ["Markets", metrics.markets], ["Latest updates", metrics.latest],
    ["Outdated prices", metrics.outdated], ["Trial users", metrics.trial], ["Active users", metrics.active], ["Feedback count", metrics.feedback],
    ["Average rating", metrics.average == null ? "—" : metrics.average.toFixed(2)],
    ["New users (7 days)", metrics.newUsersWeek], ["Referrals used", metrics.referralsUsed], ["Testimonials live", metrics.testimonialsLive],
    ["Successful payments", metrics.successfulPayments], ["Revenue (NGN)", metrics.revenue.toLocaleString("en-NG")],
  ] : [];
  return <div><div className="section-heading"><div><span className="eyebrow">Useful basics only</span><h2>Admin dashboard</h2></div></div>
    {error && <div className="status-box error">{error}</div>}
    {loading && <AdminLoading label="Loading dashboard…" />}
    <div className="admin-metric-grid">{cards.map(([label, value]) => <article className="admin-metric" key={label}><span>{label}</span><strong>{value}</strong></article>)}</div>
  </div>;
}
