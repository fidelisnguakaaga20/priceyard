import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { AdminLoading, errorText } from "./adminUtils";

type Metrics = {
  users: number; commodities: number; markets: number; latest: number; outdated: number; trial: number; active: number; feedback: number; average: number | null;
  newUsersWeek: number; referralsUsed: number; testimonialsLive: number; successfulPayments: number; revenue: number;
};

export function AdminDashboardPage() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let current = true;
    setMetrics(null); setError(""); setLoading(Boolean(token));
    if (!token) return;
    void (async () => {
    try {
      const data = await apiFetch<Omit<Metrics, "revenue"> & { revenue: string | number }>("/admin/summary", {}, token);
      if (current) setMetrics({ ...data, revenue: Number(data.revenue) });
    } catch (err) { if (current) setError(errorText(err)); }
    finally { if (current) setLoading(false); }
    })();
    return () => { current = false; };
  }, [token]);
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
