import { useState } from "react";
import { apiFetch } from "../../services/api";
import { relativeTime } from "../../utils";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";

type FlaggedPrice = {
  price_update_id: number;
  commodity_name: string;
  market_name: string;
  flag_count: number;
  latest_flag_at: string;
};

export function AdminFlaggedPricesPage() {
  const { data, loading, error: loadError, reload, token } = useAdminList<FlaggedPrice>("/price-updates/admin/flagged");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function markReviewed(priceUpdateId: number) {
    if (!token) return;
    try {
      await apiFetch(`/price-updates/${priceUpdateId}/flags/resolve`, { method: "POST" }, token);
      setMessage("Marked reviewed.");
      setError("");
      await reload();
    } catch (err) {
      setError(errorText(err));
      setMessage("");
    }
  }

  return <div>
    <h2>Flagged prices</h2>
    <p>Traders can tap "This looks off" on any price. Re-verify it, update the record if needed, then mark it reviewed to clear it from this list.</p>
    <AdminStatus error={error || loadError} success={message} />
    {loading ? <AdminLoading label="Loading flagged prices…" /> : (
      <div className="admin-card-list">
        {data.length === 0 && <p>No open flags — nothing to review right now.</p>}
        {data.map((item) => (
          <article className="card" key={item.price_update_id}>
            <div className="card-row">
              <div>
                <strong>{item.commodity_name} @ {item.market_name}</strong>
                <p>🚩 Flagged by {item.flag_count} trader{item.flag_count === 1 ? "" : "s"} — last {relativeTime(item.latest_flag_at)}</p>
              </div>
              <AdminActionButton className="button button-small" onClick={() => void markReviewed(item.price_update_id)}>Mark reviewed</AdminActionButton>
            </div>
          </article>
        ))}
      </div>
    )}
  </div>;
}
