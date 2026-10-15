import { useCallback, useEffect, useRef, useState } from "react";
import type { ButtonHTMLAttributes } from "react";
import { ButtonSpinner, LoadingSpinner } from "../../components/LoadingSpinner";
import { apiFetch, ApiError } from "../../services/api";
import { useAuth } from "../../context/AuthContext";
import { useToast } from "../../context/ToastContext";
import { adminPagePath, createLatestRequestGate, supportsAdminPaging } from "../../lib/adminPaging.mjs";

export function useAdminList<T>(path: string, paginated = true) {
  const { token } = useAuth();
  const pageSize = 100;
  const pagingEnabled = supportsAdminPaging(path, paginated);
  const [selection, setSelection] = useState({ path, page: 1 });
  const page = selection.path === path ? selection.page : 1;
  const setPage = useCallback((value: number) => setSelection({ path, page: Math.max(1, Math.floor(value) || 1) }), [path]);
  const requestPath = adminPagePath(path, page, pageSize, paginated);
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const requests = useRef(createLatestRequestGate());
  const active = useRef(true);
  const latest = useRef({ requestPath, token });
  latest.current = { requestPath, token };
  // A mutation may finish after the administrator changes page. A stable reload
  // always reads the latest selection instead of its original handler closure.
  const reload = useCallback(async (showLoader = true) => {
    if (!active.current) return;
    const request = requests.current.begin();
    const current = latest.current;
    if (!current.token) { setData([]); setLoading(false); setError(""); return; }
    if (showLoader) setLoading(true);
    setError("");
    try {
      const rows = await apiFetch<T[]>(current.requestPath, { signal: request.signal }, current.token);
      if (request.isCurrent()) setData(rows);
    } catch (err) {
      if (request.isCurrent()) setError(err instanceof ApiError ? err.detail : "Unable to load records.");
    } finally {
      if (request.isCurrent()) setLoading(false);
    }
  }, []);
  useEffect(() => {
    active.current = true;
    void reload();
    return () => { active.current = false; requests.current.cancel(); };
  }, [requestPath, token, reload]);
  const pagination = pagingEnabled ? <nav className="button-row" aria-label="Record pages">
    <button type="button" className="button button-secondary button-small" disabled={loading || page === 1} onClick={() => setPage(page - 1)}>Previous page</button>
    <span aria-live="polite">Page {page}{!loading && !error ? ` · ${data.length} record${data.length === 1 ? "" : "s"} on this page` : ""}</span>
    <button type="button" className="button button-small" disabled={loading || Boolean(error) || data.length < pageSize} onClick={() => setPage(page + 1)}>Next page</button>
  </nav> : null;
  return { data, setData, loading, error, reload, token, page, setPage, pagination };
}

export function AdminStatus({ error, success }: { error?: string; success?: string }) {
  const { showToast } = useToast();
  const lastShown = useRef<string | null>(null);
  useEffect(() => {
    const message = error || success;
    if (message && message !== lastShown.current) {
      showToast(message, error ? "error" : "success");
      lastShown.current = message;
    } else if (!message) {
      lastShown.current = null;
    }
  }, [error, success, showToast]);
  if (error) return <div className="status-box error">{error}</div>;
  if (success) return <div className="status-box success">{success}</div>;
  return null;
}

export function AdminLoading({ label = "Loading records…" }: { label?: string }) {
  return <LoadingSpinner label={label} />;
}

type AdminActionButtonProps = ButtonHTMLAttributes<HTMLButtonElement> & {
  busy?: boolean;
  busyLabel?: string;
};

export function AdminActionButton({ busy = false, busyLabel = "Please wait…", children, disabled, ...props }: AdminActionButtonProps) {
  return <button {...props} disabled={disabled || busy}>{busy ? <ButtonSpinner label={busyLabel} /> : children}</button>;
}

export function errorText(err: unknown): string {
  return err instanceof ApiError ? err.detail : err instanceof Error ? err.message : "Request failed.";
}

export function numberValue(value: FormDataEntryValue | null): number {
  return Number(String(value ?? "0"));
}

export function optionalNumber(value: FormDataEntryValue | null): number | null {
  const text = String(value ?? "").trim();
  return text ? Number(text) : null;
}
