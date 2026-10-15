import { FormEvent, useRef, useState } from "react";
import { apiFetch } from "../../services/api";
import type { FAQItem } from "../../types/api";
import { AdminActionButton, AdminLoading, AdminStatus, errorText, useAdminList } from "./adminUtils";

type FAQAdmin = FAQItem & { is_published: boolean; created_by: number };

export function AdminFAQPage() {
  const { data: items, setData, loading, error: loadError, reload, token } = useAdminList<FAQAdmin>("/faq/admin/all");
  const [targetId, setTargetId] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  const editForm = useRef<HTMLFormElement>(null);
  const select = (item: FAQAdmin) => {
    setTargetId(String(item.id));
    for (const key of ["question", "answer", "category"] as const) {
      const field = editForm.current?.elements.namedItem(key) as HTMLInputElement | HTMLTextAreaElement | null;
      if (field) field.value = item[key];
    }
    editForm.current?.querySelector<HTMLInputElement>("input")?.focus();
  };
  const remember = (item: FAQAdmin) => setData((records) => [item, ...records.filter((record) => record.id !== item.id)]);
  const save = async (event: FormEvent<HTMLFormElement>, editing: boolean) => {
    event.preventDefault();
    if (!token || busy || (editing && !targetId)) return;
    const form = event.currentTarget;
    const fields = new FormData(form);
    setBusy(true);
    try {
      const item = await apiFetch<FAQAdmin>(editing ? `/faq/${targetId}` : "/faq", {
        method: editing ? "PATCH" : "POST", body: JSON.stringify({
          question: String(fields.get("question")), answer: String(fields.get("answer")), category: String(fields.get("category")),
        }),
      }, token);
      remember(item);
      setTargetId(String(item.id));
      setMessage(`FAQ #${item.id} ${editing ? "updated" : "created hidden"}.`);
      setError("");
      form.reset();
      await reload();
    } catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  };
  const action = async (kind: "publish" | "hide" | "delete") => {
    if (!token || !targetId || busy) return;
    setBusy(true);
    try {
      if (kind === "delete") {
        await apiFetch(`/faq/${targetId}`, { method: "DELETE" }, token);
        setData((records) => records.filter((record) => String(record.id) !== targetId));
      } else remember(await apiFetch<FAQAdmin>(`/faq/${targetId}/${kind}`, { method: "PATCH" }, token));
      setMessage(`FAQ #${targetId}: ${kind} completed.`);
      setError("");
      await reload();
    } catch (err) { setError(errorText(err)); }
    finally { setBusy(false); }
  };
  const fields = <><label>Question<input name="question" required maxLength={300} /></label><label>Answer<textarea name="answer" required /></label><label>Category<input name="category" required maxLength={100} /></label></>;
  return <div>
    <h2>FAQ</h2><p className="muted">Manage published and hidden FAQs. New FAQs remain hidden until published.</p>
    <AdminStatus error={error || loadError} success={message} />
    <form className="form-stack card admin-form" onSubmit={(event) => void save(event, false)}>{fields}<AdminActionButton className="button" busy={busy}>Create hidden FAQ</AdminActionButton></form>
    <div className="admin-action-panel"><label>FAQ ID<input value={targetId} disabled={busy} onChange={(event) => setTargetId(event.target.value)} type="number" min="1" /></label><div className="button-row">{(["publish", "hide", "delete"] as const).map((kind) => <AdminActionButton key={kind} className="button button-small" busy={busy} onClick={() => void action(kind)}>{kind}</AdminActionButton>)}</div></div>
    <form ref={editForm} className="form-stack card admin-form" onSubmit={(event) => void save(event, true)}><h3>Edit selected FAQ</h3>{fields}<AdminActionButton className="button" busy={busy} disabled={!targetId}>Save FAQ</AdminActionButton></form>
    <h3>All FAQs</h3>{loading ? <AdminLoading label="Loading FAQs…" /> : <div className="admin-card-list">{items.map((item) => <article className="card" key={item.id}><span className="eyebrow">#{item.id} · {item.category} · {item.is_published ? "Published" : "Hidden"}</span><h3>{item.question}</h3><p>{item.answer}</p><button className="button button-small button-secondary" onClick={() => select(item)}>Select FAQ {item.id}</button></article>)}</div>}
  </div>;
}
