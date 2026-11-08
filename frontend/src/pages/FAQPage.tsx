import { FormEvent, useEffect, useState } from "react";
import { LoadingSpinner } from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";
import type { FAQItem } from "../types/api";

// "Updated 5 Nov 2026, 12:34 AM" in Nigeria time, matching the market insight cards.
const NIGERIA_UPDATED_FORMAT = new Intl.DateTimeFormat("en-GB", {
  timeZone: "Africa/Lagos",
  day: "numeric",
  month: "short",
  year: "numeric",
  hour: "numeric",
  minute: "2-digit",
  hour12: true,
});
function updatedLabel(value: string): string | null {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? null : `Updated ${NIGERIA_UPDATED_FORMAT.format(date)}`;
}

export function FAQPage() {
  useDocumentTitle("FAQ");
  const { token, user } = useAuth();
  const { showToast } = useToast();
  const isAdmin = user?.role === "admin" && !!token;
  const [items, setItems] = useState<FAQItem[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [busyId, setBusyId] = useState<number | null>(null);
  const [actionError, setActionError] = useState<{ id: number; text: string } | null>(null);
  useEffect(() => {
    apiFetch<FAQItem[]>("/faq")
      .then(setItems)
      .catch((err: Error) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  async function save(event: FormEvent<HTMLFormElement>, id: number) {
    event.preventDefault();
    if (!token || busyId !== null) return;
    const form = new FormData(event.currentTarget);
    setBusyId(id);
    setActionError(null);
    try {
      const updated = await apiFetch<FAQItem>(
        `/faq/${id}`,
        {
          method: "PATCH",
          body: JSON.stringify({
            question: String(form.get("question")),
            answer: String(form.get("answer")),
            category: String(form.get("category")),
          }),
        },
        token,
      );
      setItems((current) => current.map((item) => (item.id === id ? { ...item, ...updated } : item)));
      setEditingId(null);
      showToast("FAQ updated.");
    } catch (err) {
      setActionError({ id, text: err instanceof Error ? err.message : "Could not save this FAQ." });
    } finally {
      setBusyId(null);
    }
  }

  async function remove(item: FAQItem) {
    if (!token || busyId !== null || !confirm(`Delete this FAQ?\n\n"${item.question}"\n\nThis cannot be undone.`))
      return;
    setBusyId(item.id);
    setActionError(null);
    try {
      await apiFetch(`/faq/${item.id}`, { method: "DELETE" }, token);
      setItems((current) => current.filter((entry) => entry.id !== item.id));
      if (editingId === item.id) setEditingId(null);
      showToast("FAQ deleted.");
    } catch (err) {
      setActionError({ id: item.id, text: err instanceof Error ? err.message : "Could not delete this FAQ." });
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="page page-section narrow">
      <div className="page-title">
        <span className="eyebrow">PriceYard help</span>
        <h1>Frequently asked questions</h1>
        <p>Published PriceYard explanations about prices, signals, access and safe use.</p>
      </div>
      {loading ? (
        <LoadingSpinner label="Loading frequently asked questions…" />
      ) : error ? (
        <div className="status-box error">{error}</div>
      ) : items.length ? (
        <div className="faq-list">
          {items.map((item) => {
            const updated = updatedLabel(item.updated_at);
            const busy = busyId === item.id;
            const itemError =
              actionError?.id === item.id ? <div className="status-box error">{actionError.text}</div> : null;
            if (isAdmin && editingId === item.id) {
              return (
                <form
                  key={item.id}
                  className="faq-item faq-edit-form form-stack"
                  onSubmit={(event) => void save(event, item.id)}
                >
                  <label>
                    Question
                    <input name="question" defaultValue={item.question} required minLength={3} />
                  </label>
                  <label>
                    Answer
                    <textarea name="answer" defaultValue={item.answer} required minLength={3} rows={5} />
                  </label>
                  <label>
                    Category
                    <input name="category" defaultValue={item.category} required maxLength={100} />
                  </label>
                  {itemError}
                  <div className="faq-edit-buttons">
                    <button type="submit" className="button button-small" disabled={busy}>
                      {busy ? "Saving…" : "Save"}
                    </button>
                    <button
                      type="button"
                      className="button button-small button-secondary"
                      disabled={busy}
                      onClick={() => {
                        setEditingId(null);
                        setActionError(null);
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              );
            }
            return (
              <div key={item.id} className={isAdmin ? "faq-item faq-item-admin" : "faq-item"}>
                <details>
                  <summary>{item.question}</summary>
                  <div>
                    <span className="faq-meta">
                      <span className="eyebrow">{item.category}</span>
                      {updated && (
                        <time className="faq-updated" dateTime={item.updated_at}>
                          🕒 {updated}
                        </time>
                      )}
                    </span>
                    <p>{item.answer}</p>
                  </div>
                </details>
                {isAdmin && (
                  <div className="faq-admin-actions">
                    <button
                      type="button"
                      className="faq-action"
                      aria-label={`Edit FAQ: ${item.question}`}
                      disabled={busyId !== null}
                      onClick={() => {
                        setEditingId(item.id);
                        setActionError(null);
                      }}
                    >
                      ✏️<span className="faq-action-label"> Edit</span>
                    </button>
                    <button
                      type="button"
                      className="faq-action faq-action-delete"
                      aria-label={`Delete FAQ: ${item.question}`}
                      disabled={busyId !== null}
                      onClick={() => void remove(item)}
                    >
                      {busy ? (
                        "…"
                      ) : (
                        <>
                          🗑<span className="faq-action-label"> Delete</span>
                        </>
                      )}
                    </button>
                  </div>
                )}
                {itemError}
              </div>
            );
          })}
        </div>
      ) : (
        <div className="status-box">No published FAQ items are available yet.</div>
      )}
    </section>
  );
}
