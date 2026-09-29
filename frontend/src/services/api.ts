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

/** Called once by AuthProvider. When any authenticated request comes back 401, this
 * runs instead of leaving the raw error sitting in whichever page happened to make
 * the call -- it clears the stale session and sends the user back to Login. */
export function setUnauthorizedHandler(handler: (() => void) | null): void {
  unauthorizedHandler = handler;
}

export async function apiFetch<T>(
  path: string,
  options: RequestInit = {},
  token?: string | null,
): Promise<T> {
  const headers = new Headers(options.headers);
  if (options.body && !headers.has("Content-Type")) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (!response.ok) {
    let payload: unknown = null;
    try {
      payload = await response.json();
    } catch {
      payload = null;
    }
    if (response.status === 401 && token && unauthorizedHandler) {
      unauthorizedHandler();
    }
    throw new ApiError(response.status, errorDetail(payload, `Request failed with status ${response.status}`));
  }
  if (response.status === 204) return undefined as T;
  return response.json() as Promise<T>;
}

export function getApiBase(): string {
  return API_BASE;
}
