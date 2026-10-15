import { FormEvent, useState } from "react";
import { apiBlob } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { AdminActionButton, AdminStatus } from "./adminUtils";

export function AdminExportPage() {
  const { token } = useAuth();
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function submit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!token || busy) return;
    const fields = new FormData(event.currentTarget);
    const query = new URLSearchParams();
    for (const key of ["commodity", "market", "date_from", "date_to"]) {
      const value = String(fields.get(key) || "").trim();
      if (value) query.set(key, value);
    }
    setBusy(true); setError(""); setMessage("");
    try {
      const blob = await apiBlob(`/reports/prices.csv${query.size ? `?${query}` : ""}`, {}, token);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url; anchor.download = "priceyard-prices.csv";
      document.body.appendChild(anchor); anchor.click(); anchor.remove();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setMessage("CSV download started.");
    } catch (error) { setError(error instanceof Error ? error.message : "CSV export failed."); }
    finally { setBusy(false); }
  }
  return <div><h2>CSV export</h2>
    <p className="muted">Export approved observations with their recorded measurements. Dates use Nigeria time. Each file supports up to 10,000 observations; narrow the filters for larger histories.</p>
    <AdminStatus error={error} success={message} />
    <form className="form-stack card admin-form" onSubmit={submit}>
      <div className="form-grid"><label>Commodity<input name="commodity" /></label><label>Market<input name="market" /></label><label>Date from<input name="date_from" type="date" /></label><label>Date to<input name="date_to" type="date" /></label></div>
      <AdminActionButton className="button" busy={busy}>Download CSV</AdminActionButton>
    </form>
  </div>;
}
