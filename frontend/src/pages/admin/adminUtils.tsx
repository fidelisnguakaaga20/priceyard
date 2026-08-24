import { useCallback, useEffect, useState } from "react";
import type { ButtonHTMLAttributes } from "react";
import { ButtonSpinner, LoadingSpinner } from "../../components/LoadingSpinner";
import { apiFetch, ApiError } from "../../services/api";
import { useAuth } from "../../context/AuthContext";

export function useAdminList<T>(path: string) {
  const { token } = useAuth();
  const [data, setData] = useState<T[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const reload = useCallback(async () => {
    if (!token) return;
    setLoading(true); setError("");
    try { setData(await apiFetch<T[]>(path, {}, token)); }
    catch (err) { setError(err instanceof ApiError ? err.detail : "Unable to load records."); }
    finally { setLoading(false); }
  }, [path, token]);
  useEffect(() => { void reload(); }, [reload]);
  return { data, setData, loading, error, reload, token };
}

export function AdminStatus({ error, success }: { error?: string; success?: string }) {
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
