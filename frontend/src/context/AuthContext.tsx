import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, ApiError, setUnauthorizedHandler } from "../services/api";
import { useToast } from "./ToastContext";
import type { Subscription, User } from "../types/api";
import { accessExpiresAt, computeAccess } from "../services/access";
import type { AccessLabel } from "../services/access";
import { finishLogout } from "../services/push";
import { browserSession, rememberBrowserSession, forgetBrowserSession, SESSION_EVENT_KEY, LOGOUT_PENDING_KEY, signalSessionChange } from "../services/sessionTransport";
import type { BrowserSession } from "../services/sessionTransport";

type AuthContextValue = {
  user: User | null;
  subscription: Subscription | null;
  token: string | null;
  loading: boolean;
  accessLabel: AccessLabel;
  hasFullAccess: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  register: (payload: { full_name: string; email: string; phone?: string; password: string; referral_code?: string }) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const STORAGE_KEY = "priceyard_access_token";
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

// Only used once to convert existing valid credentials without extending expiry.
function readLegacyToken(): { token: string; remember: boolean } | null {
  try {
    const persistent = localStorage.getItem(STORAGE_KEY);
    const transient = sessionStorage.getItem(STORAGE_KEY);
    return persistent ? { token: persistent, remember: true } : transient ? { token: transient, remember: false } : null;
  } catch { return null; }
}
function pendingLogout(): string | null {
  try { return localStorage.getItem(LOGOUT_PENDING_KEY); } catch { return null; }
}
function setPendingLogout(value: string | null): void {
  try { if (value) localStorage.setItem(LOGOUT_PENDING_KEY, value); else localStorage.removeItem(LOGOUT_PENDING_KEY); } catch { /* view still clears immediately */ }
}

function clearStoredToken(): void {
  try {
    localStorage.removeItem(STORAGE_KEY);
    sessionStorage.removeItem(STORAGE_KEY);
  } catch {
    // ignore
  }
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(true);
  const expiredHandledRef = useRef(false);
  const activeTokenRef = useRef(token);
  const refreshSequence = useRef(0);
  const authSequence = useRef(0);
  const signInPending = useRef(false);
  const profileReady = useRef(false);
  const [accessTick, setAccessTick] = useState(0);
  const access = computeAccess(user, subscription);

  useEffect(() => {
    const updateAccess = () => setAccessTick((tick) => tick + 1);
    const expiresAt = accessExpiresAt(subscription);
    // Passive effects can run after the deadline crossed during rendering.
    // Recheck once instead of leaving the last active render without a timer.
    if (expiresAt !== null && Number.isFinite(expiresAt) && expiresAt <= Date.now() && access.full && user?.role !== "admin") updateAccess();
    const timer = expiresAt !== null && Number.isFinite(expiresAt) && expiresAt > Date.now()
      ? window.setTimeout(updateAccess, Math.min(expiresAt - Date.now() + 1, 2_147_000_000))
      : undefined;
    window.addEventListener("focus", updateAccess);
    document.addEventListener("visibilitychange", updateAccess);
    return () => {
      window.clearTimeout(timer);
      window.removeEventListener("focus", updateAccess);
      document.removeEventListener("visibilitychange", updateAccess);
    };
  }, [subscription, accessTick, access.full, user?.role]);

  const clearAuth = useCallback(() => {
    ++authSequence.current;
    ++refreshSequence.current;
    activeTokenRef.current = null;
    profileReady.current = false;
    clearStoredToken();
    setToken(null);
    setUser(null);
    setSubscription(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (token) expiredHandledRef.current = false;
  }, [token]);

  useEffect(() => {
    setUnauthorizedHandler((failedToken) => {
      if (failedToken !== activeTokenRef.current) return;
      if (expiredHandledRef.current) return;
      expiredHandledRef.current = true;
      clearAuth();
      showToast("Your session expired — please log in again.", "error");
      navigate("/login");
    });
    return () => setUnauthorizedHandler(null);
  }, [clearAuth, navigate, showToast]);

  const refreshWithToken = useCallback(async (activeToken: string) => {
    if (activeTokenRef.current !== activeToken) return;
    const sequence = ++refreshSequence.current;
    const isCurrent = () => sequence === refreshSequence.current && activeTokenRef.current === activeToken;
    if (!profileReady.current) setLoading(true);
    try {
      const currentUser = await apiFetch<User>("/auth/me", {}, activeToken);
      if (!isCurrent()) return;
      let currentSubscription: Subscription | null | undefined;
      try {
        currentSubscription = await apiFetch<Subscription>(`/subscriptions/${currentUser.id}`, {}, activeToken);
      } catch (error) {
        if (error instanceof ApiError && [401, 403].includes(error.status)) throw error;
        if (error instanceof ApiError && error.status === 404) currentSubscription = null;
      }
      if (!isCurrent()) return;
      setUser(currentUser);
      if (currentSubscription !== undefined) setSubscription(currentSubscription);
      profileReady.current = true;
    } catch (error) {
      if (isCurrent() && error instanceof ApiError && [401, 403].includes(error.status)) clearAuth();
    } finally {
      if (isCurrent()) setLoading(false);
    }
  }, [clearAuth]);

  useEffect(() => {
    if (token) void refreshWithToken(token);
  }, [token, refreshWithToken]);

  const adoptSession = useCallback(async (session: BrowserSession) => {
    const current = activeTokenRef.current;
    if (current && browserSession(current)?.session_id === session.session_id) {
      await refreshWithToken(current);
      return;
    }
    const handle = rememberBrowserSession(session);
    activeTokenRef.current = handle;
    profileReady.current = false;
    setUser(null);
    setSubscription(null);
    setToken(handle);
    clearStoredToken();
    await refreshWithToken(handle);
  }, [refreshWithToken]);

  const resumeBrowserSession = useCallback(async () => {
    const sequence = ++authSequence.current;
    const pendingAtStart = pendingLogout();
    try {
      let session: BrowserSession;
      try { session = await apiFetch<BrowserSession>("/auth/browser/session"); }
      catch (error) {
        const legacy = readLegacyToken();
        if (!(error instanceof ApiError) || error.status !== 401 || !legacy || pendingLogout()) throw error;
        try {
          session = await apiFetch<BrowserSession>("/auth/browser/upgrade", {
            method: "POST", body: JSON.stringify({ remember: legacy.remember }),
          }, legacy.token);
        } catch (upgradeError) {
          if (upgradeError instanceof ApiError && [401, 403].includes(upgradeError.status)) clearStoredToken();
          throw upgradeError;
        }
      }
      if (sequence !== authSequence.current) return;
      const pending = pendingLogout();
      if (pending) {
        const handle = rememberBrowserSession(session);
        const confirmed = await finishLogout(handle, () => activeTokenRef.current === null);
        forgetBrowserSession(handle);
        if (sequence !== authSequence.current) return;
        if (confirmed && pendingLogout() === pending) setPendingLogout(null);
        clearAuth();
        return;
      }
      await adoptSession(session);
    } catch (error) {
      if (sequence !== authSequence.current) return;
      if (error instanceof ApiError && [401, 403].includes(error.status)) {
        // An old tab's 401 cannot acknowledge a logout created while its
        // request was in flight. Only the marker this request started with
        // can be cleared by confirmation that no browser login remains.
        if (pendingAtStart && pendingLogout() === pendingAtStart) setPendingLogout(null);
        clearAuth();
      } else setLoading(false);
    }
  }, [adoptSession, clearAuth]);

  useEffect(() => { void resumeBrowserSession(); }, [resumeBrowserSession]);
  useEffect(() => {
    const changed = (event: StorageEvent) => {
      if (event.key !== SESSION_EVENT_KEY && event.key !== LOGOUT_PENDING_KEY) return;
      // Completion of an older logout in another tab must not cancel a new
      // explicit sign-in waiting for the shared cookie-mutation lock.
      if (signInPending.current) return;
      clearAuth();
      if (!pendingLogout()) void resumeBrowserSession();
    };
    const reconnect = () => { if (!signInPending.current && pendingLogout()) void resumeBrowserSession(); };
    const focus = () => { if (signInPending.current) return; if (!pendingLogout()) void resumeBrowserSession(); else reconnect(); };
    window.addEventListener("storage", changed);
    window.addEventListener("online", reconnect);
    window.addEventListener("focus", focus);
    return () => {
      window.removeEventListener("storage", changed);
      window.removeEventListener("online", reconnect);
      window.removeEventListener("focus", focus);
    };
  }, [clearAuth, resumeBrowserSession]);

  const login = async (email: string, password: string, remember = true) => {
    const sequence = ++authSequence.current;
    signInPending.current = true;
    try {
    const response = await apiFetch<BrowserSession>("/auth/browser/login", {
      method: "POST", body: JSON.stringify({ email, password, remember }),
    });
    if (sequence !== authSequence.current) return;
    setPendingLogout(null);
    await adoptSession(response);
    signalSessionChange();
    } finally { signInPending.current = false; }
  };

  const loginWithGoogle = async (idToken: string) => {
    const sequence = ++authSequence.current;
    signInPending.current = true;
    try {
    const response = await apiFetch<BrowserSession>("/auth/browser/google", {
      method: "POST", body: JSON.stringify({ id_token: idToken, remember: true }),
    });
    if (sequence !== authSequence.current) return;
    setPendingLogout(null);
    await adoptSession(response);
    signalSessionChange();
    } finally { signInPending.current = false; }
  };

  const register = async (payload: { full_name: string; email: string; phone?: string; password: string; referral_code?: string }) => {
    await apiFetch<User>("/auth/register", { method: "POST", body: JSON.stringify(payload) });
    await login(payload.email, payload.password);
  };

  const refresh = async () => {
    if (token) await refreshWithToken(token);
  };

  const logout = useCallback(() => {
    const currentToken = activeTokenRef.current;
    clearAuth();
    if (currentToken) {
      setPendingLogout(currentToken);
      signalSessionChange();
      // Local logout stays immediate. Only this device is cleaned up, and a
      // late worker lookup must never disable a newly signed-in account.
      void finishLogout(currentToken, () => activeTokenRef.current === null).then(confirmed => {
        forgetBrowserSession(currentToken);
        if (confirmed && pendingLogout() === currentToken) {
          setPendingLogout(null);
          signalSessionChange();
        }
      });
    }
  }, [clearAuth]);

  const value = useMemo<AuthContextValue>(() => ({
    user,
    subscription,
    token,
    loading,
    accessLabel: access.label,
    hasFullAccess: access.full,
    login,
    loginWithGoogle,
    register,
    logout,
    refresh,
  }), [user, subscription, token, loading, access.label, access.full, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
