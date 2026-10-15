import { coalescePublicRead } from "../lib/publicRequests.mjs";
const API_BASE = (import.meta.env.VITE_API_URL as string | undefined)?.replace(/\/$/, "") || "/api";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string) {
    super(detail);
    this.status = status;
    this.detail = detail;
  }
}

function errorDetail(payload: unknown, fallback: string): string {
  if (payload && typeof payload === "object" && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail.map((item) => (item && typeof item === "object" && "msg" in item ? String(item.msg) : String(item))).join("; ");
    }
  }
  return fallback;
}

let unauthorizedHandler: (() => void) | null = null;
let refreshHandler: (() => Promise<string | null>) | null = null;

export function setRefreshHandler(handler: (() => Promise<string | null>) | null): void {
  refreshHandler = handler;
}

/** Called once by AuthProvider. When any authenticated request comes back 401, this
 * runs instead of leaving the raw error sitting in whichever page happened to make
 * the call -- it clears the stale session and sends the user back to Login. */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

async function performApiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
  recoverSession = true,
  responseType: "json" | "blob" = "json",
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const timeout = new AbortController();
  const timer = setTimeout(() => timeout.abort(), 20_000);
  const cancel = () => timeout.abort();
  if (options.signal?.aborted) cancel();
  else options.signal?.addEventListener("abort", cancel, { once: true });
  try {
    const response = await fetch(`${API_BASE}${path}`, { ...options, headers, signal: timeout.signal });
    if (response.headers.get("X-PriceYard-Cached") === "true") {
      window.dispatchEvent(new CustomEvent("priceyard:cached-data", { detail: response.headers.get("X-PriceYard-Cached-At") }));
    }
    if (response.status === 401 && token && recoverSession && refreshHandler) {
      const refreshed = await refreshHandler();
      if (refreshed) return performApiFetch<T>(path, options, refreshed, false, responseType);
    }
    if (!response.ok) {
      let payload: unknown = null;
      try {
        payload = await response.json();
      } catch {
        payload = null;
      }
      if (response.status === 401 && token && recoverSession && unauthorizedHandler) {
        unauthorizedHandler();
      }
      throw new ApiError(response.status, errorDetail(payload, `Request failed with status ${response.status}`));
    }
    if (response.status === 204) return undefined as T;
    return (responseType === "blob" ? await response.blob() : await response.json()) as T;
  } finally {
    clearTimeout(timer);
    options.signal?.removeEventListener("abort", cancel);
  }
}

export function apiFetch<T>(path: string, options: RequestInit = {}, token?: string | null, recoverSession = true): Promise<T> {
  const publicRead = !token && !options.signal && !options.headers && !options.body
    && (!options.method || options.method === "GET") && options.credentials !== "include"
    && options.cache !== "no-store" && /^\/(price-updates|commodities|markets)(?:\?|$)/.test(path);
  const load = () => performApiFetch<T>(path, options, token, recoverSession);
  return publicRead ? coalescePublicRead(API_BASE + path, load) : load();
}

export function getApiBase(): string {
  return API_BASE;
}

export function apiBlob(path: string, options: RequestInit = {}, token?: string | null): Promise<Blob> {
  return performApiFetch<Blob>(path, options, token, true, "blob");
}
