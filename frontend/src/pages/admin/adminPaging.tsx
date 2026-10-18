import { useCallback, useEffect, useRef, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { useAuth } from "../../context/AuthContext";
import { apiFetch, ApiError } from "../../services/api";

type RecordPage<T> = { items: T[]; total: number; offset: number; limit: number };

export function useAdminPagedList<T>(path: string) {
  const { token } = useAuth();
  const [searchParams, setSearchParams] = useSearchParams();
  const requestedOffset = Number(searchParams.get("offset") || 0);
  const offset = Number.isSafeInteger(requestedOffset) && requestedOffset >= 0 && requestedOffset <= 2_147_483_647 ? requestedOffset : 0;
  const [result, setResult] = useState<{ path: string; token: string; page: RecordPage<T> } | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const sequence = useRef(0);
  const active = useRef({ path, token, offset });
  active.current = { path, token, offset };
  const move = useCallback((value: number, replace = false) => {
    sequence.current++; setLoading(true); setError("");
    setSearchParams(previous => {
      const next = new URLSearchParams(previous);
      if (value) next.set("offset", String(value)); else next.delete("offset");
      return next;
    }, { replace });
  }, [setSearchParams]);

  const reload = useCallback(async () => {
    const request = ++sequence.current;
    if (!token) { setResult(null); setLoading(false); return; }
    setLoading(true); setError("");
    const current = () => request === sequence.current && active.current.path === path && active.current.token === token && active.current.offset === offset;
    try {
      const page = await apiFetch<RecordPage<T>>(`${path}${path.includes("?") ? "&" : "?"}offset=${offset}`, {}, token);
      if (!current()) return;
      if (offset > 0 && !page.items.length) {
        const last = page.total ? Math.floor((page.total - 1) / page.limit) * page.limit : 0;
        if (last !== offset) { move(last, true); return; }
      }
      setResult({ path, token, page });
    } catch (err) {
      if (current()) setError(err instanceof ApiError ? err.detail : "Unable to load records.");
    } finally {
      if (current()) setLoading(false);
    }
  }, [path, token, offset, move]);
  useEffect(() => { void reload(); return () => { sequence.current++; }; }, [reload]);
  const owned = result?.path === path && result.token === token ? result.page : null;
  const data = owned?.offset === offset ? owned.items : [];
  const total = owned?.total ?? 0;
  const limit = owned?.limit ?? 100;
  return { data, total, loading, error, reload, token, offset, limit,
    previous: () => move(Math.max(0, offset - limit)), next: () => move(offset + limit) };
}

type PageControls = { total: number; offset: number; limit: number; loading: boolean; previous: () => void; next: () => void };

export function AdminPagination({ page, label }: { page: PageControls; label: string }) {
  if (page.total <= page.limit && !page.offset) return null;
  const start = page.total ? page.offset + 1 : 0;
  const end = Math.min(page.offset + page.limit, page.total);
  return <nav className="filter-actions top-gap" aria-label={`${label} pages`}>
    <button className="button button-small button-ghost" type="button" disabled={page.loading || !page.offset} onClick={page.previous}>Previous</button>
    <span className="muted" aria-live="polite">Showing {start}–{end} of {page.total}</span>
    <button className="button button-small button-ghost" type="button" disabled={page.loading || page.offset + page.limit >= page.total} onClick={page.next}>Next</button>
  </nav>;
}
