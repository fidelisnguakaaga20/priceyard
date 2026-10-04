import { useEffect, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { relativeTime } from "../../utils";
import type { ActivitySummary } from "../../types/api";
import { AdminLoading, errorText } from "./adminUtils";

const EVENT_LABEL: Record<string, string> = {
  app_visit: "Opened the app",
  share_view: "Opened a shared price link",
};

export function AdminActivityPage() {
  const { token } = useAuth();
  const [summary, setSummary] = useState<ActivitySummary | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => { if (!token) return; void (async () => {
    try {
      const data = await apiFetch<ActivitySummary>("/activity/summary", {}, token);
      setSummary(data);
      if (data.unseen_count > 0) await apiFetch("/activity/seen", { method: "POST" }, token);
    } catch (err) { setError(errorText(err)); }
    finally { setLoading(false); }
  })(); }, [token]);

  return <div>
    <h2>Visitor activity</h2>
    <p>Anonymous app opens and shared-link clicks — no visitor identity is collected, just counts of what's being checked.</p>
    {error && <div className="status-box error">{error}</div>}
    {loading ? <AdminLoading label="Loading activity…" /> : (
      <div className="admin-card-list">
        {summary && summary.recent.length === 0 && <p>No activity recorded yet.</p>}
        {summary?.recent.map((event) => (
          <article className="card" key={event.id}>
            <div className="card-row">
              <div>
                <strong>{EVENT_LABEL[event.event_type] || event.event_type}</strong>
                {event.label && <p>{event.label}</p>}
              </div>
              <small>{relativeTime(event.created_at)}</small>
            </div>
          </article>
        ))}
      </div>
    )}
  </div>;
}
