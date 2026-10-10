import { FormEvent, useEffect, useRef, useState } from "react";
import { apiFetch } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useCommodityMarketPairs } from "../../hooks/useCommodityMarketPairs";
import type { Commodity, Market, PriceUpdateAdmin } from "../../types/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";

const actions = ["Watch", "Investigate", "Buy Carefully", "Hold", "Sell Carefully"];
const movements = ["up", "down", "stable", "unknown"];
const confidenceLevels = ["Reporter submitted", "Verified by 2 sources", "Admin confirmed", "Market visit confirmed", "Low confidence", "Price outdated"];
const marketDays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
const timesOfDay = ["morning", "afternoon", "evening", "closing"];

export function AdminPriceUpdatesPage() {
  const { token } = useAuth();
  const { data: history, loading, error: loadError, reload } = useAdminList<PriceUpdateAdmin>("/price-updates/admin/history");
  const [commodities, setCommodities] = useState<Commodity[]>([]); const [markets, setMarkets] = useState<Market[]>([]);
  const [created, setCreated] = useState<PriceUpdateAdmin[]>([]); const [error, setError] = useState(""); const [message, setMessage] = useState(""); const [targetId, setTargetId] = useState("");
  const [busy, setBusy] = useState(false); const [optionsLoading, setOptionsLoading] = useState(true);
  const commodityMarketPairs = useCommodityMarketPairs();
  const [newCommodityId, setNewCommodityId] = useState("");
  const [showCreateExtra, setShowCreateExtra] = useState(false);
  const [showCorrectExtra, setShowCorrectExtra] = useState(false);
  const newCommodityName = commodities.find((c) => String(c.id) === newCommodityId)?.name;
  const knownMarketNames = newCommodityName ? commodityMarketPairs.get(newCommodityName) : undefined;
  const createFormRef = useRef<HTMLFormElement>(null);

  useEffect(() => { if (!token) return; setOptionsLoading(true); void Promise.all([apiFetch<Commodity[]>("/commodities", {}, token), apiFetch<Market[]>("/markets", {}, token)]).then(([c,m]) => { setCommodities(c); setMarkets(m); }).catch((err) => setError(errorText(err))).finally(() => setOptionsLoading(false)); }, [token]);

  async function create(e: FormEvent<HTMLFormElement>) { e.preventDefault(); if (!token || busy) return; const f = new FormData(e.currentTarget); const payload = {
    commodity_id: Number(f.get("commodity_id")), market_id: Number(f.get("market_id")), price_low: Number(f.get("price_low")), price_high: Number(f.get("price_high")), average_price: Number(f.get("average_price")), previous_price_low: String(f.get("previous_price_low") || "") ? Number(f.get("previous_price_low")) : null, previous_price_high: String(f.get("previous_price_high") || "") ? Number(f.get("previous_price_high")) : null,
    unit: String(f.get("unit")), bag_size: String(f.get("bag_size") || "") || null, commodity_type: String(f.get("commodity_type") || "") || null, market_day: String(f.get("market_day") || "") || null, time_of_day: String(f.get("time_of_day") || "") || null, movement: String(f.get("movement")), confidence_level: String(f.get("confidence_level")), source_type: String(f.get("source_type") || "") || null, source_1: String(f.get("source_1") || "") || null, source_2: String(f.get("source_2") || "") || null, update_date_time: String(f.get("update_date_time")), is_outdated: false, possible_meaning: String(f.get("possible_meaning") || "") || null, suggested_action: String(f.get("suggested_action")), notes: String(f.get("notes") || "") || null,
  }; setBusy(true); try { const item = await apiFetch<PriceUpdateAdmin>("/price-updates", { method: "POST", body: JSON.stringify(payload) }, token); setCreated((items) => [item, ...items]); setTargetId(String(item.id)); setMessage(`Price update #${item.id} created pending approval.`); setError(""); } catch (err) { setError(errorText(err)); setMessage(""); } finally { setBusy(false); } }

  function prefillFromLast() {
    const form = createFormRef.current;
    if (!form) return;
    const marketId = (form.elements.namedItem("market_id") as HTMLSelectElement | null)?.value;
    if (!newCommodityId || !marketId) { setError("Choose a commodity and market first, then prefill."); return; }
    const last = [...created, ...history]
      .filter((r) => String(r.commodity_id) === newCommodityId && String(r.market_id) === marketId)
      .sort((a, b) => new Date(b.update_date_time).getTime() - new Date(a.update_date_time).getTime())[0];
    if (!last) { setError(`No previous record found for this commodity/market pair to prefill from.`); return; }
    const setField = (name: string, value: string) => { const el = form.elements.namedItem(name) as HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement | null; if (el) el.value = value; };
    setField("unit", last.unit);
    setField("bag_size", last.bag_size || "");
    setField("commodity_type", last.commodity_type || "");
    setField("market_day", last.market_day || "");
    setField("time_of_day", last.time_of_day || "");
    setField("movement", last.movement);
    setField("confidence_level", last.confidence_level);
    setField("source_type", last.source_type || "");
    setField("source_1", last.source_1 || "");
    setField("source_2", last.source_2 || "");
    setField("suggested_action", last.suggested_action || "Watch");
    setField("possible_meaning", last.possible_meaning || "");
    setField("notes", last.notes || "");
    setField("previous_price_low", String(last.price_low));
    setField("previous_price_high", String(last.price_high));
    setError("");
    setMessage(`Prefilled from record #${last.id} (${last.update_date_time.slice(0, 10)}). Enter the new price and date, then create.`);
  }

  async function act(action: "approve"|"reject"|"mark-outdated"|"delete") { if (!token || !targetId || busy) return; setBusy(true); try { if (action === "delete") await apiFetch(`/price-updates/${targetId}`, { method: "DELETE" }, token); else await apiFetch(`/price-updates/${targetId}/${action}`, { method: "PATCH" }, token); setMessage(`Price update #${targetId}: ${action} completed.`); setError(""); await reload(); } catch (err) { setError(errorText(err)); } finally { setBusy(false); } }

  async function editRecord(e: FormEvent<HTMLFormElement>) {
    e.preventDefault();
    if (!token || busy) return;
    if (!targetId) { setError("Select a price-update row or enter a Record ID before saving a correction."); setMessage(""); return; }

    const form = e.currentTarget;
    const f = new FormData(form);
    const payload: Record<string, string | number> = {};
    const addNumber = (field: string) => { const value = String(f.get(field) || "").trim(); if (value !== "") payload[field] = Number(value); };
    const addString = (field: string) => { const value = String(f.get(field) || "").trim(); if (value !== "") payload[field] = value; };

    ["price_low", "price_high", "average_price", "previous_price_low", "previous_price_high"].forEach(addNumber);
    ["unit", "bag_size", "market_day", "time_of_day", "movement", "confidence_level", "update_date_time", "source_type", "possible_meaning", "suggested_action", "notes"].forEach(addString);

    if (!Object.keys(payload).length) { setError("Enter at least one field to correct. Blank fields are left unchanged."); setMessage(""); return; }

    setBusy(true);
    try {
      await apiFetch(`/price-updates/${targetId}`, { method: "PATCH", body: JSON.stringify(payload) }, token);
      setMessage(`Price update #${targetId} corrected. Approval status was preserved.`);
      setError("");
      form.reset();
      await reload();
    } catch (err) {
      setError(errorText(err));
      setMessage("");
    } finally {
      setBusy(false);
    }
  }

  const rows = [...created, ...history.filter((h) => !created.some((c) => c.id === h.id))];

  return <div><h2>Price updates</h2><p className="muted">Create records, correct existing records, approve/reject, mark outdated, or delete by record ID. The admin list below includes pending, approved and rejected records so pending updates remain available for approval after refresh.</p><AdminStatus error={error || loadError} success={message} />
    <form className="form-stack card admin-form" onSubmit={create} ref={createFormRef}><div className="button-row"><AdminActionButton className="button button-secondary button-small" type="button" busy={busy} disabled={optionsLoading} onClick={prefillFromLast}>Prefill from last entry</AdminActionButton></div><div className="form-grid"><label>Commodity<select name="commodity_id" required disabled={optionsLoading} onChange={(e) => setNewCommodityId(e.target.value)}><option value="">Choose a commodity</option>{commodities.map((x) => <option value={x.id} key={x.id}>{x.name}</option>)}</select></label><label>Market<select name="market_id" required disabled={optionsLoading}>{knownMarketNames ? <><optgroup label={`Markets with an existing ${newCommodityName} price`}>{markets.filter((x) => knownMarketNames.has(x.name)).map((x) => <option value={x.id} key={x.id}>{x.name}</option>)}</optgroup><optgroup label="Other markets (no price for this commodity yet)">{markets.filter((x) => !knownMarketNames.has(x.name)).map((x) => <option value={x.id} key={x.id}>{x.name}</option>)}</optgroup></> : markets.map((x) => <option value={x.id} key={x.id}>{x.name}</option>)}</select>{newCommodityName && <small className="muted">Markets already carrying {newCommodityName} are listed first.</small>}</label><label>Low<input name="price_low" type="number" min="0" step="0.01" required /></label><label>High<input name="price_high" type="number" min="0" step="0.01" required /></label><label>Average<input name="average_price" type="number" min="0" step="0.01" required /></label><label>Number of bags<input name="unit" defaultValue="1 bag" placeholder="e.g. 1 bag" required /></label><label>Previous low<input name="previous_price_low" type="number" min="0" step="0.01" /></label><label>Previous high<input name="previous_price_high" type="number" min="0" step="0.01" /></label><label>Bag size (kg)<input name="bag_size" placeholder="e.g. 50kg" required /></label><label>Market day<select name="market_day"><option value="">Unknown</option>{marketDays.map((d) => <option key={d}>{d}</option>)}</select></label><label>Time of day<select name="time_of_day"><option value="">Unknown</option>{timesOfDay.map((d) => <option key={d}>{d}</option>)}</select></label><label>Movement<select name="movement" defaultValue="unknown">{movements.map((x) => <option key={x}>{x}</option>)}</select></label><label>Confidence<select name="confidence_level" defaultValue="Reporter submitted">{confidenceLevels.map((x) => <option key={x}>{x}</option>)}</select></label><label>Update date/time<input name="update_date_time" type="datetime-local" required /></label></div><label>Possible Meaning <small>(optional)</small><textarea name="possible_meaning" placeholder="Leave blank if you have no specific observation" /></label><label>Suggested Action<select name="suggested_action">{actions.map((x) => <option key={x}>{x}</option>)}</select></label>
      <button type="button" className="text-link text-link-button" onClick={() => setShowCreateExtra((v) => !v)}>{showCreateExtra ? "− Hide extra fields" : "+ Show extra fields (commodity type, sources, notes)"}</button>
      <div className="form-grid" style={showCreateExtra ? undefined : { display: "none" }}><label>Commodity type<input name="commodity_type" /></label><label>Source type<input name="source_type" /></label><label>Source 1 (private)<input name="source_1" /></label><label>Source 2 (private)<input name="source_2" /></label></div>
      <label style={showCreateExtra ? undefined : { display: "none" }}>Notes<textarea name="notes" /></label>
      <AdminActionButton className="button" type="submit" busy={busy} disabled={optionsLoading}>Create pending update</AdminActionButton></form>

    <div className="admin-action-panel"><label>Record ID<input value={targetId} disabled={busy} onChange={(e) => setTargetId(e.target.value)} inputMode="numeric" /></label><div className="button-row"><AdminActionButton className="button button-small" busy={busy} onClick={() => void act("approve")}>Approve</AdminActionButton><AdminActionButton className="button button-small button-secondary" busy={busy} onClick={() => void act("reject")}>Reject</AdminActionButton><AdminActionButton className="button button-small button-secondary" busy={busy} onClick={() => void act("mark-outdated")}>Mark outdated</AdminActionButton><AdminActionButton className="button button-small button-danger" busy={busy} onClick={() => void act("delete")}>Delete</AdminActionButton></div></div>

    <form className="form-stack card admin-form" onSubmit={editRecord}>
      <h3>Correct existing price record</h3>
      <p className="muted">Uses the Record ID above. Enter only the fields that need correction; blank fields stay unchanged. Saving does not change pending/approved/rejected status.</p>
      <div className="form-grid">
        <label>Number of bags<input name="unit" placeholder="No change" /></label>
        <label>Bag size (kg)<input name="bag_size" placeholder="No change" /></label>
        <label>Low<input name="price_low" type="number" min="0" step="0.01" placeholder="No change" /></label>
        <label>High<input name="price_high" type="number" min="0" step="0.01" placeholder="No change" /></label>
        <label>Average<input name="average_price" type="number" min="0" step="0.01" placeholder="No change" /></label>
        <label>Previous low<input name="previous_price_low" type="number" min="0" step="0.01" placeholder="No change" /></label>
        <label>Previous high<input name="previous_price_high" type="number" min="0" step="0.01" placeholder="No change" /></label>
        <label>Market day<select name="market_day" defaultValue=""><option value="">No change</option>{marketDays.map((d) => <option key={d}>{d}</option>)}</select></label>
        <label>Time of day<select name="time_of_day" defaultValue=""><option value="">No change</option>{timesOfDay.map((d) => <option key={d}>{d}</option>)}</select></label>
        <label>Movement<select name="movement" defaultValue=""><option value="">No change</option>{movements.map((x) => <option key={x}>{x}</option>)}</select></label>
        <label>Confidence<select name="confidence_level" defaultValue=""><option value="">No change</option>{confidenceLevels.map((x) => <option key={x}>{x}</option>)}</select></label>
        <label>Update date/time<input name="update_date_time" type="datetime-local" /></label>
      </div>
      <label>Possible Meaning<textarea name="possible_meaning" placeholder="No change" /></label>
      <label>Suggested Action<select name="suggested_action" defaultValue=""><option value="">No change</option>{actions.map((x) => <option key={x}>{x}</option>)}</select></label>
      <button type="button" className="text-link text-link-button" onClick={() => setShowCorrectExtra((v) => !v)}>{showCorrectExtra ? "− Hide extra fields" : "+ Show extra fields (source type, notes)"}</button>
      <div className="form-grid" style={showCorrectExtra ? undefined : { display: "none" }}><label>Source type<input name="source_type" placeholder="No change" /></label></div>
      <label style={showCorrectExtra ? undefined : { display: "none" }}>Notes<textarea name="notes" placeholder="No change" /></label>
      <AdminActionButton className="button" type="submit" busy={busy}>Save correction</AdminActionButton>
    </form>

    {loading || optionsLoading ? <AdminLoading label="Loading price-update data…" /> : <div className="table-wrap"><table className="admin-table"><thead><tr><th>ID</th><th>Commodity / market</th><th>Range</th><th>Status</th><th>Meaning / action</th></tr></thead><tbody>{rows.map((item) => <tr key={item.id} onClick={() => setTargetId(String(item.id))}><td>{item.id}</td><td>{item.commodity?.name || item.commodity_id}<small>{item.market?.name || item.market_id}</small></td><td>{item.price_low} – {item.price_high}</td><td>{item.status}{item.is_outdated ? " · outdated" : ""}</td><td>{item.possible_meaning}<small>{item.suggested_action}</small></td></tr>)}</tbody></table></div>}
  </div>;
}
