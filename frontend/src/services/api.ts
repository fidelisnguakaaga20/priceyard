import { browserSession, serializeCookieMutation } from "./sessionTransport";
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

let unauthorizedHandler: ((failedToken: string) => void) | null = null;

/** Called once by AuthProvider. When any authenticated request comes back 401, this
 * runs instead of leaving the raw error sitting in whichever page happened to make
 * the call -- it clears the stale session and sends the user back to Login. */
export function setUnauthorizedHandler(handler: ((failedToken: string) => void) | null): void {
  unauthorizedHandler = handler;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
  onProvenance?: (savedAt: string | null) => void,
  format: "json" | "blob" = "json",
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  const cookie = Boolean(token?.startsWith("cookie:"));
  if (cookie && token) {
    const session = browserSession(token);
    if (!session) throw new ApiError(401, "Browser session changed");
    headers.set("X-PriceYard-Session", session.session_id);
    headers.set("X-PriceYard-CSRF", session.csrf_token);
  } else if (token) headers.set("Authorization", `Bearer ${token}`);

  const send = () => fetch(`${API_BASE}${path}`, { ...options, headers,
    credentials: cookie || path.startsWith("/auth/browser/") ? "include" : "omit",
    ...((cookie || path.startsWith("/auth/browser/")) ? { cache: "no-store" as RequestCache } : {}) });
  const cookieMutation = (cookie && path === "/auth/logout") || ["/auth/browser/login", "/auth/browser/google", "/auth/browser/upgrade"].includes(path);
  const response = await (cookieMutation ? serializeCookieMutation(send) : send());
  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    if (response.status === 401 && token && unauthorizedHandler) {
      unauthorizedHandler(token);
    }
    throw new ApiError(response.status, errorDetail(payload, `Request failed with status ${response.status}`));
  }
  const cached = response.headers.get("X-PriceYard-Cache") === "saved";
  const stamp = response.headers.get("X-PriceYard-Saved-At");
  const parsed = Date.parse(stamp || "");
  if (cached && (!Number.isFinite(parsed) || new Date(parsed).toISOString() !== stamp)) {
    // A legacy/invalid saved copy has no trustworthy device-save timestamp.
    throw new ApiError(503, "Request failed with status 503");
  }
  const data = response.status === 204 ? undefined as T : await (format === "blob" ? response.blob() : response.json()) as T;
  onProvenance?.(cached ? stamp : null);
  return data;
}

export async function apiFetchWithProvenance<T>(path: string): Promise<{ data: T; savedAt: string | null }> {
  let savedAt: string | null = null;
  const data = await apiFetch<T>(path, {}, null, value => { savedAt = value; });
  return { data, savedAt };
}

export function getApiBase(): string {
  return API_BASE;
}
