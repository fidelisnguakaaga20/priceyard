import { FormEvent, useState } from "react";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";

export function FeedbackPage() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [rating, setRating] = useState(5);
  const [suggestion, setSuggestion] = useState("");
  const [continueUsing, setContinueUsing] = useState<boolean | null>(null);
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (!token || busy) return;

    if (continueUsing === null) {
      setError("Please choose Yes or No");
      setMessage("");
      return;
    }

    setBusy(true);
    setError("");
    setMessage("");
    try {
      await apiFetch(
        "/feedback",
        {
          method: "POST",
          body: JSON.stringify({
            rating,
            complaint_or_suggestion: suggestion || null,
            continue_using_feedback: continueUsing,
          }),
        },
        token,
      );
      setMessage("Thank you. Your feedback was submitted.");
      setSuggestion("");
      setContinueUsing(null);
      showToast("Thank you. Your feedback was submitted.");
    } catch (err) {
      setError((err as Error).message);
      showToast((err as Error).message, "error");
    } finally {
      setBusy(false);
    }
  };

  return <section className="page page-section narrow">
    <div className="page-title">
      <span className="eyebrow">User feedback</span>
      <h1>Rate your PriceYard experience</h1>
      <p>Your rating must be between 1 and 5. Share a complaint or suggestion to help improve PriceYard.</p>
    </div>
    <form className="form-stack card" onSubmit={submit}>
      <fieldset>
        <legend>Overall rating</legend>
        <div className="rating-row">
          {[1, 2, 3, 4, 5].map((value) =>
            <label key={value} className={rating === value ? "rating-option selected" : "rating-option"}>
              <input type="radio" name="rating" checked={rating === value} onChange={() => setRating(value)} />
              {value} ★
            </label>
          )}
        </div>
      </fieldset>
      <label>
        Complaint or suggestion
        <textarea rows={4} value={suggestion} onChange={(e) => setSuggestion(e.target.value)} />
      </label>
      <label>
        Continue using?
        <select value={continueUsing === null ? "" : String(continueUsing)} onChange={(e) => setContinueUsing(e.target.value === "" ? null : e.target.value === "true")}>
          <option value="">No answer</option>
          <option value="true">Yes</option>
          <option value="false">No</option>
        </select>
      </label>
      {message && <div className="status-box success">{message}</div>}
      {error && <div className="status-box error">{error}</div>}
      <button className="button" disabled={busy}>
        {busy ? <ButtonSpinner label="Please wait…" /> : "Submit feedback"}
      </button>
    </form>
  </section>;
}
