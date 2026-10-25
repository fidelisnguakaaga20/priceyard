import { useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiFetch } from "../../services/api";
import type { Subscription } from "../../types/api";
import { AdminPagination, useAdminPagedList } from "./adminPaging";
import { AdminActionButton, AdminLoading, AdminStatus, errorText } from "./adminUtils";
import "./owner-permissions.css";

export function AdminSubscriptionsPage() {
  const { user: currentUser } = useAuth();
  const page = useAdminPagedList<Subscription>("/subscriptions/admin/page");
  const { data, loading, error: loadError, reload, token } = page;
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busyUserId, setBusyUserId] = useState<number | null>(null);
  const [remindersBusy, setRemindersBusy] = useState(false);

  async function update(userId: number, status: string) {
    if (!token || busyUserId !== null) return;
    setBusyUserId(userId);
    try {
      await apiFetch(`/subscriptions/${userId}/status`, { method: "PATCH", body: JSON.stringify({ status }) }, token);
      setMessage(`Subscription for user #${userId} updated.`); setError("");
      await reload();
    } catch (err) { setError(errorText(err)); }
    finally { setBusyUserId(null); }
  }

  async function sendReminders() {
    if (!token || remindersBusy) return;
    setRemindersBusy(true);
    try {
      const result = await apiFetch<{ sent: number }>("/subscriptions/send-trial-reminders", { method: "POST" }, token);
      setMessage(`Trial-expiry reminder emails sent: ${result.sent}.`); setError("");
    } catch (err) { setError(errorText(err)); }
    finally { setRemindersBusy(false); }
  }

  return <div>
    <h2>Subscriptions</h2>
    <p className="muted">Manage subscription status. Owner access does not require a subscription.</p>
    <AdminStatus error={error || loadError} success={message} />
    <div className="admin-action-panel">
      <span className="muted">Emails any trial user whose trial ends within 3 days and hasn't already been reminded.</span>
      <AdminActionButton className="button button-small button-secondary" busy={remindersBusy} onClick={sendReminders}>Send trial-expiry reminders</AdminActionButton>
    </div>
    {busyUserId !== null && <AdminLoading label={`Updating subscription for user #${busyUserId}…`} />}
    {loading ? <AdminLoading label="Loading subscriptions…" /> : <div className="table-wrap"><table className="admin-table">
      <thead><tr><th>User</th><th>Plan</th><th>Status</th><th>Trial ends</th></tr></thead>
      <tbody>{data.map((subscription) => {
        const isOwnOwnerRecord = currentUser?.is_owner === true && currentUser.role === "admin" && currentUser.id === subscription.user_id;
        return <tr key={subscription.id} data-owner={isOwnOwnerRecord}>
          <td>#{subscription.user_id}{isOwnOwnerRecord && <><br /><span className="owner-account-badge">Owner</span></>}</td>
          <td>{subscription.plan_name}</td>
          <td>
            <select aria-label={`Subscription status for user #${subscription.user_id}`} value={subscription.status} disabled={busyUserId !== null}
              onChange={(event) => void update(subscription.user_id, event.target.value)}>
              {["free", "trial", "active", "expired", "cancelled"].map((status) => <option key={status}>{status}</option>)}
            </select>
            {isOwnOwnerRecord && <small className="owner-account-note">Owner access does not expire. This subscription record is kept for history.</small>}
          </td>
          <td>{subscription.trial_ends_at ? new Date(subscription.trial_ends_at).toLocaleString() : "—"}</td>
        </tr>;
      })}</tbody>
    </table></div>}
    <AdminPagination page={page} label="Subscriptions" />
  </div>;
}
