import { FormEvent, useCallback, useEffect, useRef, useState } from "react";
import { useAuth } from "../../context/AuthContext";
import { apiFetch } from "../../services/api";
import { money, shortDate } from "../../utils";
import { AdminLoading, AdminStatus, errorText } from "./adminUtils";

type Payment = { id: number; user_id: number; reference: string; plan: string; amount: string | number;
  currency: string; status: string; duration_days: number; created_at: string;
  access_applied: boolean; requires_reconciliation: boolean; reconciliation_error: string | null;
  entitlement_applied_at: string | null; granted_expires_at: string | null };
type Resolution = "" | "already_applied" | "apply_missing";
const LIMIT = 100;
const outcomes: Record<string, string> = {
  applied: "The verified purchase was applied. Payment and access were recorded together.",
  already_applied: "The purchase is recorded as already applied. No additional access was granted.",
  review_required: "No access was granted. This historical payment needs an explicit reviewed disposition.",
  evidence_mismatch: "No access was granted. The signed evidence does not match the stored purchase; review the payment details.",
  unknown_reference: "No matching purchase was found. No access was granted.",
  ignored_event: "This evidence is not a successful charge event. No access was granted.",
};

export function AdminPaymentsPage() {
  const { token } = useAuth();
  const [items, setItems] = useState<Payment[]>([]);
  const [nextOffset, setNextOffset] = useState(0);
  const [more, setMore] = useState(false);
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [signedPayload, setSignedPayload] = useState("");
  const [signature, setSignature] = useState("");
  const [reason, setReason] = useState("");
  const [resolution, setResolution] = useState<Resolution>("");
  const generation = useRef(0);
  const load = useCallback(async (offset: number, reset = false) => {
    if (!token) return;
    const attempt = ++generation.current;
    setLoading(true);
    try {
      const records = await apiFetch<Payment[]>(`/payments?offset=${offset}&limit=${LIMIT}`, {}, token);
      if (attempt !== generation.current) return;
      setItems((current) => reset ? records : [...current, ...records.filter((record) => !current.some((item) => item.id === record.id))]);
      setNextOffset(offset + records.length); setMore(records.length === LIMIT); setError("");
    } catch (err) { if (attempt === generation.current) setError(errorText(err)); }
    finally { if (attempt === generation.current) setLoading(false); }
  }, [token]);
  useEffect(() => { void load(0, true); return () => { ++generation.current; }; }, [load]);
  let reference = "";
  try { const event = JSON.parse(signedPayload); if (typeof event?.data?.reference === "string") reference = event.data.reference; } catch { /* Exact raw input is validated by the server. */ }
  const selected = items.find((item) => item.reference === reference);
  const reconcile = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || busy) return;
    setBusy(true); setMessage(""); setError("");
    try {
      const result = await apiFetch<{ outcome: string }>("/payments/reconcile", { method: "POST", body: JSON.stringify({
        signed_payload: signedPayload, signature: signature.trim(), reason: reason.trim(), legacy_resolution: resolution || null,
      }) }, token);
      setMessage(outcomes[result.outcome] || `Reconciliation returned: ${result.outcome}`);
      // Raw evidence is never persisted in browser storage or echoed into the report.
      if (result.outcome === "applied" || result.outcome === "already_applied") {
        setSignedPayload(""); setSignature(""); setReason(""); setResolution("");
      }
      await load(0, true);
    } catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  };

  return <div>
    <h2>Payments</h2><p className="muted">A confirmed payment and applied access are shown separately. Historical payments marked for review are never automatically granted a second time.</p>
    <AdminStatus error={error} success={message} />
    <div className="button-row"><button className="button button-small button-secondary" disabled={loading || busy} onClick={() => void load(0, true)}>Refresh payments</button><span>{items.length} records loaded</span></div>
    {loading && <AdminLoading label="Loading payments…" />}
    <div className="table-wrap"><table className="admin-table">
      <thead><tr><th>Time (Nigeria)</th><th>User</th><th>Plan / term</th><th>Amount</th><th>Payment</th><th>Access</th><th>Reference / review</th></tr></thead>
      <tbody>{items.map((item) => <tr key={item.id}>
        <td>{shortDate(item.created_at)}</td><td>User #{item.user_id}</td><td>{item.plan}<small>{item.duration_days} days</small></td><td>{money(item.amount)}</td><td>{item.status}</td>
        <td>{item.requires_reconciliation ? "Review required" : item.access_applied ? "Recorded as applied" : "Not yet applied"}<small>{item.granted_expires_at ? `Paid cutoff: ${shortDate(item.granted_expires_at)}` : ""}</small></td>
        <td><small>{item.reference}</small>{item.reconciliation_error && <small>{item.reconciliation_error.replace(/_/g, " ")}</small>}</td>
      </tr>)}</tbody>
    </table></div>
    {more && <button className="button button-small" disabled={loading || busy} onClick={() => void load(nextOffset)}>Load older payments</button>}
    <details className="card top-gap"><summary>Review signed payment evidence</summary>
      <p>Use evidence already obtained through your authorized payment-provider records. This form does not contact Paystack. Never paste a secret key.</p>
      <p>Paste the exact signed JSON without reformatting it. Its reference, amount, currency, customer and provider outcome must match the stored purchase.</p>
      <form className="form-stack" onSubmit={reconcile}>
        <label>Exact signed event JSON<textarea required maxLength={32768} rows={8} spellCheck={false} autoComplete="off" value={signedPayload} onChange={(event) => setSignedPayload(event.target.value)} /></label>
        {reference && <p>Reference: {reference}{selected?.requires_reconciliation ? " · historical review required" : ""}</p>}
        <label>Provider signature<input required pattern="[0-9a-fA-F]{128}" maxLength={128} spellCheck={false} autoComplete="off" value={signature} onChange={(event) => setSignature(event.target.value)} /></label>
        <label>Historical disposition<select required={selected?.requires_reconciliation} value={resolution} onChange={(event) => setResolution(event.target.value as Resolution)}><option value="">Reprocess verified evidence without a historical decision</option><option value="already_applied">Reviewed: access was already applied; do not extend</option><option value="apply_missing">Reviewed: purchased access was missing; apply once</option></select></label>
        <p className="muted">Choose a historical disposition only after checking retained business evidence. The server still verifies the signed provider event.</p>
        <label>Review reason<textarea required minLength={10} maxLength={500} value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        <button className="button" disabled={busy || loading}>{busy ? "Reviewing…" : "Validate evidence and record reviewed outcome"}</button>
      </form>
    </details>
  </div>;
}
