// These handles/CSRF values cannot authenticate without the HttpOnly cookie.
export type BrowserSession = { session_id: string; csrf_token: string };
const sessions = new Map<string, BrowserSession>();
export function rememberBrowserSession(session: BrowserSession): string {
  const handle = `cookie:${session.session_id}:${crypto.randomUUID()}`;
  sessions.set(handle, session);
  if (sessions.size > 32) sessions.delete(sessions.keys().next().value!);
  return handle;
}
export function browserSession(handle: string): BrowserSession | undefined { return sessions.get(handle); }
export function forgetBrowserSession(handle: string): void { sessions.delete(handle); }
export const SESSION_EVENT_KEY = "priceyard_session_event";
export const LOGOUT_PENDING_KEY = "priceyard_logout_pending";
export function signalSessionChange(): void {
  try { localStorage.setItem(SESSION_EVENT_KEY, crypto.randomUUID()); } catch { /* focus still refreshes the session */ }
}

export function serializeCookieMutation<T>(send: () => Promise<T>): Promise<T> {
  // A delayed logout response must not erase a more recent sign-in cookie.
  // Web Locks serializes cookie-changing requests across this browser's tabs.
  if (typeof navigator !== "undefined" && navigator.locks) {
    return navigator.locks.request("priceyard-browser-session", send);
  }
  // A tab-only queue would silently lose the cross-tab safety guarantee.
  return Promise.reject(new Error("Protected browser sessions need an updated browser. Please update your browser and try again."));
}
