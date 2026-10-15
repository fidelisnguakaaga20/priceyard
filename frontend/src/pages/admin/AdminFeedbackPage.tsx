import { useCallback, useEffect, useRef, useState } from "react";
import { apiFetch } from "../../services/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";
import { createLatestRequestGate } from "../../lib/adminPaging.mjs";

type Feedback = {
  id: number;
  user_id: number;
  rating: number;
  comment: string | null;
  complaint_or_suggestion: string | null;
  missing_market_request: string | null;
  missing_commodity_request: string | null;
  continue_using_feedback: boolean | null;
  is_public_testimonial: boolean;
  testimonial_display_name: string | null;
  screenshot_data: string | null;
  created_at: string;
};
type Summary = { count: number; average_rating: number | null };

export function AdminFeedbackPage() {
  const [rating, setRating] = useState("");
  const { data: items, token, loading, error: loadError, reload, pagination } = useAdminList<Feedback>(rating ? `/feedback?rating=${rating}` : "/feedback");
  const [summary, setSummary] = useState<Summary | null>(null);
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [removingId, setRemovingId] = useState<number | null>(null);
  const [testimonialBusyId, setTestimonialBusyId] = useState<number | null>(null);
  const [displayNames, setDisplayNames] = useState<Record<number, string>>({});

  const summaryRequests = useRef(createLatestRequestGate());
  const summaryActive = useRef(true);
  const currentToken = useRef(token);
  currentToken.current = token;
  const loadSummary = useCallback(async () => {
    if (!summaryActive.current) return;
    const request = summaryRequests.current.begin();
    if (!currentToken.current) { setSummary(null); return; }
    try {
      const feedbackSummary = await apiFetch<Summary>("/feedback/summary", { signal: request.signal }, currentToken.current);
      if (request.isCurrent()) setSummary(feedbackSummary);
    } catch (err) {
      if (request.isCurrent()) setError(errorText(err));
    }
  }, []);

  useEffect(() => {
    summaryActive.current = true;
    void loadSummary();
    return () => { summaryActive.current = false; summaryRequests.current.cancel(); };
  }, [token, loadSummary]);
  const load = useCallback(async (showLoader = true) => { await Promise.all([reload(showLoader), loadSummary()]); }, [reload, loadSummary]);

  async function remove(id: number) {
    if (!token || removingId !== null || !confirm("Delete this feedback?")) return;
    setRemovingId(id);
    try {
      await apiFetch(`/feedback/${id}`, { method: "DELETE" }, token);
      setMessage("Feedback deleted.");
      setError("");
      await load(false);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setRemovingId(null);
    }
  }

  async function publishTestimonial(id: number) {
    if (!token || testimonialBusyId !== null) return;
    const displayName = (displayNames[id] || "").trim();
    if (!displayName) {
      setError("Enter a display name before featuring this feedback as a testimonial.");
      return;
    }
    setTestimonialBusyId(id);
    try {
      await apiFetch(`/feedback/${id}/testimonial/publish`, { method: "PATCH", body: JSON.stringify({ display_name: displayName }) }, token);
      setMessage(`Feedback #${id} is now a public testimonial.`);
      setError("");
      await load(false);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setTestimonialBusyId(null);
    }
  }

  async function hideTestimonial(id: number) {
    if (!token || testimonialBusyId !== null) return;
    setTestimonialBusyId(id);
    try {
      await apiFetch(`/feedback/${id}/testimonial/hide`, { method: "PATCH" }, token);
      setMessage(`Feedback #${id} removed from public testimonials.`);
      setError("");
      await load(false);
    } catch (err) {
      setError(errorText(err));
    } finally {
      setTestimonialBusyId(null);
    }
  }

  return <div>
    <h2>Feedback</h2>
    <div className="admin-metric-grid">
      <article className="admin-metric"><span>Feedback count</span><strong>{summary?.count ?? "—"}</strong></article>
      <article className="admin-metric"><span>Average rating</span><strong>{summary?.average_rating == null ? "—" : summary.average_rating.toFixed(2)}</strong></article>
    </div>
    <label className="admin-inline-filter">Filter rating<select value={rating} disabled={loading || removingId !== null} onChange={(e) => setRating(e.target.value)}><option value="">All</option>{[1, 2, 3, 4, 5].map((x) => <option key={x}>{x}</option>)}</select></label>
    <AdminStatus error={error || loadError} success={message} />
    {loading ? <AdminLoading label="Loading feedback…"/> : <div className="admin-card-list">{items.map((item) => <article className="card" key={item.id}><div className="card-row"><div><span className="eyebrow">#{item.id} · {item.rating}/5 · user #{item.user_id}</span><h3>{item.comment || "Feedback"}</h3><p>{item.complaint_or_suggestion || "No complaint/suggestion"}</p><small>Continue using: {item.continue_using_feedback === null ? "No answer" : item.continue_using_feedback ? "Yes" : "No"}</small><small>{item.missing_market_request ? `Market request: ${item.missing_market_request}` : ""} {item.missing_commodity_request ? `Commodity request: ${item.missing_commodity_request}` : ""}</small>{item.screenshot_data && <p><a href={item.screenshot_data} target="_blank" rel="noopener noreferrer"><img src={item.screenshot_data} alt="Feedback screenshot" className="feedback-screenshot-thumb" /></a></p>}</div><AdminActionButton className="button button-small button-danger" busy={removingId === item.id} disabled={removingId !== null && removingId !== item.id} onClick={() => void remove(item.id)}>Delete</AdminActionButton></div>
      <div className="admin-testimonial-row">
        {item.is_public_testimonial ? (
          <>
            <span className="badge badge-success">Public testimonial as "{item.testimonial_display_name}"</span>
            <AdminActionButton className="button button-small button-secondary" busy={testimonialBusyId === item.id} disabled={testimonialBusyId !== null && testimonialBusyId !== item.id} onClick={() => void hideTestimonial(item.id)}>Remove from testimonials</AdminActionButton>
          </>
        ) : (
          <>
            <input
              type="text"
              placeholder="Display name (e.g. Mvendaga N.)"
              maxLength={100}
              value={displayNames[item.id] || ""}
              disabled={testimonialBusyId !== null}
              onChange={(e) => setDisplayNames((prev) => ({ ...prev, [item.id]: e.target.value }))}
            />
            <AdminActionButton className="button button-small" busy={testimonialBusyId === item.id} disabled={testimonialBusyId !== null && testimonialBusyId !== item.id} onClick={() => void publishTestimonial(item.id)}>Feature as public testimonial</AdminActionButton>
          </>
        )}
      </div>
    </article>)}</div>}
    {pagination}
  </div>;
}

