import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { shortDate } from "../../utils";
import { AdminLoading, errorText } from "./adminUtils";

type Metrics = {
  generated_at: string; users_total: number; users_active: number; users_new_seven_days: number; users_referred: number;
  commodities_total: number; commodities_active: number; markets_total: number; markets_active: number;
  prices_total: number; prices_current: number; prices_pending: number; prices_approved: number; prices_rejected: number;
  prices_withdrawn: number; prices_outdated: number; open_flags: number; flagged_prices: number;
  subscription_statuses: Record<string, number>; valid_trial_subscriptions: number; valid_paid_subscriptions: number;
  feedback_count: number; feedback_average_rating: string | null; testimonials_live: number;
  payments_total: number; payments_pending: number; payments_failed: number; payments_recorded_success: number;
  payments_provider_confirmed: number; payments_access_applied: number; payments_requires_review: number;
  recorded_success_amount_ngn: string; recorded_success_amounts: Record<string, string>;
};

function decimalAmount(value: string): string {
  const [whole, fraction = ""] = value.split(".");
  return `${whole.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}.${fraction.padEnd(2, "0")}`;
}

export function AdminDashboardPage() {
  const { token } = useAuth();
  const [metrics, setMetrics] = useState<Metrics | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [attempt, setAttempt] = useState(0);
  useEffect(() => {
    if (!token) { setMetrics(null); setLoading(false); return; }
    const controller = new AbortController();
    setLoading(true); setError("");
    void apiFetch<Metrics>("/admin/metrics", { signal: controller.signal }, token)
      .then((data) => { if (!controller.signal.aborted) setMetrics(data); })
      .catch((err) => { if (!controller.signal.aborted) setError(errorText(err)); })
      .finally(() => { if (!controller.signal.aborted) setLoading(false); });
    return () => controller.abort();
  }, [token, attempt]);
  const cards: [string, string | number][] = metrics ? [
    ["Total users", metrics.users_total], ["Active accounts", metrics.users_active],
    ["New users (7 days)", metrics.users_new_seven_days], ["Accounts with referrals", metrics.users_referred],
    ["Commodities", metrics.commodities_total], ["Active commodities", metrics.commodities_active],
    ["Markets", metrics.markets_total], ["Active markets", metrics.markets_active],
    ["Current measurement series", metrics.prices_current], ["Pending observations", metrics.prices_pending],
    ["Marked outdated records", metrics.prices_outdated], ["Prices with open flags", metrics.flagged_prices],
    ["Unresolved flags", metrics.open_flags], ["Valid trial accounts", metrics.valid_trial_subscriptions],
    ["Valid paid/manual accounts", metrics.valid_paid_subscriptions], ["Feedback count", metrics.feedback_count],
    ["Average rating", metrics.feedback_average_rating === null ? "—" : metrics.feedback_average_rating],
    ["Testimonials live", metrics.testimonials_live], ["Payment records", metrics.payments_total],
    ["Recorded successful payments", metrics.payments_recorded_success], ["Verified provider confirmations", metrics.payments_provider_confirmed],
    ["Access application recorded", metrics.payments_access_applied], ["Payments needing review", metrics.payments_requires_review],
    ["Pending payments", metrics.payments_pending], ["Failed payments", metrics.payments_failed],
    ["Recorded successful amount (NGN)", decimalAmount(metrics.recorded_success_amount_ngn)],
    ...Object.entries(metrics.recorded_success_amounts).filter(([currency]) => currency !== "NGN")
      .map(([currency, amount]): [string, string] => [`Recorded successful amount (${currency})`, decimalAmount(amount)]),
  ] : [];
  return <div>
    <div className="section-heading"><div><span className="eyebrow">Business records</span><h2>Admin dashboard</h2></div><button className="button button-small button-secondary" disabled={loading} onClick={() => setAttempt((value) => value + 1)}>Refresh counts</button></div>
    {error && <div className="status-box error">{error}{metrics && " Previously loaded counts remain below."}</div>}
    {loading && <AdminLoading label="Loading dashboard counts…" />}
    {metrics && <p className="muted">Generated {shortDate(metrics.generated_at)} (Nigeria time). Counts include all stored records, independent of list pagination.</p>}
    <div className="admin-metric-grid">{cards.map(([label, value]) => <article className="admin-metric" key={label}><span>{label}</span><strong>{value}</strong></article>)}</div>
    {metrics && <>
      <p className="muted">Stored subscription labels: {Object.entries(metrics.subscription_statuses).map(([label, count]) => `${label}: ${count}`).join(" · ")}. Valid-access counts also check expiry and account activity.</p>
      <p className="muted">Recorded successful amounts sum stored payment records; they are not a bank settlement or refund statement. Historical review and access application are reported separately.</p>
    </>}
  </div>;
}
