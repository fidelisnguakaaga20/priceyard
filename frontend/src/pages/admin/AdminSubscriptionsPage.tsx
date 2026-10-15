import { useState } from "react";
import { apiFetch } from "../../services/api";
import type { Subscription } from "../../types/api";
import { shortDate } from "../../utils";
import { paidCutoffValue } from "../../lib/priceSeries.mjs";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";

export function AdminSubscriptionsPage() {
  const { data, loading, error: loadError, reload, token, pagination } = useAdminList<Subscription>("/subscriptions");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyUserId, setBusyUserId] = useState<number | null>(null);
  const [remindersBusy, setRemindersBusy] = useState(false);
  const update = async (userId: number, status: string) => {
    if (!token || busyUserId !== null) return;
    setBusyUserId(userId);
    try {
      await apiFetch(`/subscriptions/${userId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }, token);
      setMessage(`Subscription for user #${userId} updated.`); setError(""); await reload();
    } catch (err) { setError(errorText(err)); }
    finally { setBusyUserId(null); }
  };
  const sendReminders = async () => {
    if (!token || remindersBusy) return;
    setRemindersBusy(true);
    try {
      const result = await apiFetch<{ sent: number }>("/subscriptions/send-trial-reminders", { method: "POST" }, token);
      setMessage(`Trial-expiry reminders accepted for delivery: ${result.sent}.`); setError("");
    } catch (err) { setError(errorText(err)); }
    finally { setRemindersBusy(false); }
  };
  return <div>
    <h2>Subscriptions</h2><p className="muted">Payments activate access automatically after verified evidence. Manual active grants remain indefinite. Subscription changes preserve valid purchased time and staff authority; cancellation records intent without deleting paid access.</p>
    <AdminStatus error={error || loadError} success={message} />
    <div className="admin-action-panel"><span className="muted">Request reminders for eligible trial users whose access ends within three days.</span><AdminActionButton className="button button-small button-secondary" busy={remindersBusy} onClick={() => void sendReminders()}>Send trial-expiry reminders</AdminActionButton></div>
    {busyUserId !== null && <AdminLoading label={`Updating user #${busyUserId}…`} />}
    {loading ? <AdminLoading label="Loading subscriptions…" /> : <div className="table-wrap"><table className="admin-table">
      <thead><tr><th>User</th><th>Plan</th><th>Status</th><th>Trial cutoff (Nigeria)</th><th>Paid cutoff (Nigeria)</th><th>Cancellation request</th></tr></thead>
      <tbody>{data.map((item) => <tr key={item.id}><td>#{item.user_id}</td><td>{item.plan_name}</td><td><select aria-label={`Subscription status for user ${item.user_id}`} value={item.status} disabled={busyUserId !== null} onChange={(event) => void update(item.user_id, event.target.value)}>{["free", "trial", "active", "expired", "cancelled"].map((value) => <option key={value}>{value}</option>)}</select></td><td>{shortDate(item.trial_ends_at)}</td><td>{item.manual_grant || (item.status === "active" && !item.paid_expires_at && !item.end_date) ? "Manual grant: no expiry" : shortDate(paidCutoffValue(item))}</td><td>{shortDate(item.cancellation_requested_at)}</td></tr>)}</tbody>
    </table></div>}
    {pagination}
  </div>;
}
