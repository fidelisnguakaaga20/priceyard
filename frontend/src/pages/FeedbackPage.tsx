import { FormEvent, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { apiFetch } from "../services/api";

export function FeedbackPage() {
  const { token } = useAuth();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState("");
  const [usefulness, setUsefulness] = useState("");
  const [accuracy, setAccuracy] = useState("");
  const [missingMarket, setMissingMarket] = useState("");
  const [missingCommodity, setMissingCommodity] = useState("");
  const [suggestion, setSuggestion] = useState("");
  const [continueUsing, setContinueUsing] = useState<boolean | null>(null);
  const [willingPay, setWillingPay] = useState<boolean | null>(null);
  const [message, setMessage] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  const submit = async (event: FormEvent) => { event.preventDefault(); if (!token) return; setBusy(true); setError(""); setMessage(""); try { await apiFetch("/feedback", { method: "POST", body: JSON.stringify({ rating, comment: comment || null, price_usefulness: usefulness || null, price_accuracy: accuracy || null, missing_market_request: missingMarket || null, missing_commodity_request: missingCommodity || null, complaint_or_suggestion: suggestion || null, continue_using_feedback: continueUsing, willingness_to_pay_feedback: willingPay }) }, token); setMessage("Thank you. Your feedback was submitted."); setComment(""); setSuggestion(""); } catch (err) { setError((err as Error).message); } finally { setBusy(false); } };
  return <section className="page page-section narrow"><div className="page-title"><span className="eyebrow">User feedback</span><h1>Rate your PriceYard experience</h1><p>Your rating must be between 1 and 5. Feedback helps improve the MVP without adding unapproved features.</p></div>
    <form className="form-stack card" onSubmit={submit}><fieldset><legend>Overall rating</legend><div className="rating-row">{[1,2,3,4,5].map((value) => <label key={value} className={rating === value ? "rating-option selected" : "rating-option"}><input type="radio" name="rating" checked={rating === value} onChange={() => setRating(value)} />{value} ★</label>)}</div></fieldset><label>Comment<textarea rows={3} value={comment} onChange={(e) => setComment(e.target.value)} /></label><div className="form-grid"><label>Price usefulness<input value={usefulness} onChange={(e) => setUsefulness(e.target.value)} placeholder="Useful / very useful…" /></label><label>Price accuracy feedback<input value={accuracy} onChange={(e) => setAccuracy(e.target.value)} placeholder="Your observation" /></label><label>Missing market request<input value={missingMarket} onChange={(e) => setMissingMarket(e.target.value)} /></label><label>Missing commodity request<input value={missingCommodity} onChange={(e) => setMissingCommodity(e.target.value)} /></label></div><label>Complaint or suggestion<textarea rows={3} value={suggestion} onChange={(e) => setSuggestion(e.target.value)} /></label><div className="form-grid"><label>Continue using?<select value={continueUsing === null ? "" : String(continueUsing)} onChange={(e) => setContinueUsing(e.target.value === "" ? null : e.target.value === "true")}><option value="">No answer</option><option value="true">Yes</option><option value="false">No</option></select></label><label>Willingness to pay?<select value={willingPay === null ? "" : String(willingPay)} onChange={(e) => setWillingPay(e.target.value === "" ? null : e.target.value === "true")}><option value="">No answer</option><option value="true">Yes</option><option value="false">No</option></select></label></div>{message && <div className="status-box success">{message}</div>}{error && <div className="status-box error">{error}</div>}<button className="button" disabled={busy}>{busy ? "Submitting…" : "Submit feedback"}</button></form>
  </section>;
}
