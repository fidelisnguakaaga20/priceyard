import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, ApiError, setRefreshHandler, setUnauthorizedHandler } from "../services/api";
import { useToast } from "./ToastContext";
import type { Subscription, User } from "../types/api";

type AccessLabel = "Guest" | "Free" | "Trial" | "Active Paid" | "Admin";
type Credentials = { access_token: string; refresh_token: string; expires_in: number; session_expires_at: string };
type AuthContextValue = {
  user: User | null; subscription: Subscription | null; token: string | null;
  loading: boolean; accessLabel: AccessLabel; hasFullAccess: boolean;
  login: (email: string, password: string, remember?: boolean) => Promise<void>;
  loginWithGoogle: (idToken: string, remember?: boolean) => Promise<void>;
  register: (payload: { full_name: string; email: string; phone?: string; password: string; referral_code?: string }) => Promise<void>;
  logout: () => void; refresh: () => Promise<void>;
};
const ACCESS_KEY = "priceyard_access_token";
const REFRESH_KEY = "priceyard_refresh_token";
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function stored(key: string): string | null {
  try { return sessionStorage.getItem(key) || localStorage.getItem(key); } catch { return null; }
}
function persist(credentials: Credentials, remember: boolean) {
  try {
    const target = remember ? localStorage : sessionStorage;
    const other = remember ? sessionStorage : localStorage;
    other.removeItem(REFRESH_KEY); target.setItem(REFRESH_KEY, credentials.refresh_token);
    localStorage.removeItem(ACCESS_KEY); sessionStorage.removeItem(ACCESS_KEY);
  } catch { /* Session works in memory when storage is unavailable. */ }
}
function clearStorage() {
  try { for (const key of [ACCESS_KEY, REFRESH_KEY]) { localStorage.removeItem(key); sessionStorage.removeItem(key); } } catch { /* unavailable */ }
}
export function computeAccess(user: User | null, subscription: Subscription | null, now = Date.now()): { label: AccessLabel; full: boolean } {
  if (!user) return { label: "Guest", full: false };
  if (user.role === "admin") return { label: "Admin", full: true };
  if (subscription?.status === "trial" && subscription.trial_ends_at && new Date(subscription.trial_ends_at).getTime() > now) return { label: "Trial", full: true };
  if (subscription?.status === "active") {
    const expiry = subscription.paid_expires_at ? new Date(subscription.paid_expires_at).getTime()
      : subscription.end_date ? Date.parse(subscription.end_date + "T00:00:00Z") + 86_400_000 : Infinity;
    if (now < expiry) return { label: "Active Paid", full: true };
  }
  return { label: "Free", full: false };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [token, setToken] = useState<string | null>(null);
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(Boolean(stored(REFRESH_KEY) || stored(ACCESS_KEY)));
  const [clock, setClock] = useState(Date.now());
  const tokenRef = useRef<string | null>(null);
  const refreshRef = useRef<string | null>(stored(REFRESH_KEY));
  const rememberRef = useRef(false);
  const rotating = useRef<Promise<string | null> | null>(null);
  const generation = useRef(0);
  const profileReady = useRef(false);
  const clearAuth = useCallback(() => {
    generation.current++; profileReady.current = false; clearStorage(); tokenRef.current = null; refreshRef.current = null;
    setToken(null); setUser(null); setSubscription(null); setLoading(false);
    navigator.serviceWorker?.controller?.postMessage({ type: "CLEAR_USER_STATE" });
  }, []);
  const accept = useCallback((credentials: Credentials, remember: boolean) => {
    rememberRef.current = remember; refreshRef.current = credentials.refresh_token;
    tokenRef.current = credentials.access_token; setToken(credentials.access_token); persist(credentials, remember);
  }, []);
  const rotate = useCallback(async (): Promise<string | null> => {
    if (!refreshRef.current) return null;
    if (rotating.current) return rotating.current;
    const currentGeneration = generation.current;
    rotating.current = (async () => {
      try {
        const credentials = await apiFetch<Credentials>("/auth/refresh", { method: "POST", body: JSON.stringify({ refresh_token: refreshRef.current }) }, null, false);
        if (currentGeneration !== generation.current) return null;
        accept(credentials, rememberRef.current); return credentials.access_token;
      } catch (error) {
        if (error instanceof ApiError && [400, 401, 403].includes(error.status)) { clearAuth(); return null; }
        throw error;
      } finally { rotating.current = null; }
    })();
    return rotating.current;
  }, [accept, clearAuth]);
  const loadProfile = useCallback(async (activeToken: string) => {
    const currentGeneration = generation.current;
    // Refreshing an established account must not unmount protected screens
    // (including a payment callback waiting for this same refresh to finish).
    if (!profileReady.current) setLoading(true);
    try {
      const profile = await apiFetch<User>("/auth/me", {}, activeToken);
      let access: Subscription | null = null;
      try { access = await apiFetch<Subscription>("/subscriptions/" + profile.id, {}, tokenRef.current || activeToken); }
      catch (error) { if (!(error instanceof ApiError && error.status === 404)) throw error; }
      if (currentGeneration !== generation.current) return;
      profileReady.current = true;
      setUser(profile); setSubscription(access); setClock(Date.now());
    } catch (error) {
      if (error instanceof ApiError && [401, 403].includes(error.status)) clearAuth();
      throw error;
    } finally { if (currentGeneration === generation.current) setLoading(false); }
  }, [clearAuth]);
  useEffect(() => {
    setRefreshHandler(rotate);
    setUnauthorizedHandler(() => { clearAuth(); showToast("Please sign in again to continue.", "error"); navigate("/login"); });
    return () => { setRefreshHandler(null); setUnauthorizedHandler(null); };
  }, [rotate, clearAuth, showToast, navigate]);
  useEffect(() => {
    try { rememberRef.current = Boolean(localStorage.getItem(REFRESH_KEY)); } catch { /* unavailable */ }
    if (refreshRef.current) void rotate().then((value) => { if (value) return loadProfile(value); }).catch(() => { setLoading(false); showToast("Could not restore your account. Please retry when connected.", "error"); });
    else { clearStorage(); setLoading(false); }
  }, [rotate, loadProfile, showToast]);
  useEffect(() => {
    const timer = setInterval(() => setClock(Date.now()), 10_000);
    return () => clearInterval(timer);
  }, []);
  const login = async (email: string, password: string, remember = false) => {
    generation.current++;
    const credentials = await apiFetch<Credentials>("/auth/login", { method: "POST", body: JSON.stringify({ email, password, remember_me: remember }) });
    accept(credentials, remember); await loadProfile(credentials.access_token);
  };
  const loginWithGoogle = async (idToken: string, remember = false) => {
    generation.current++;
    const credentials = await apiFetch<Credentials>("/auth/google", { method: "POST", body: JSON.stringify({ id_token: idToken, remember_me: remember }) });
    accept(credentials, remember); await loadProfile(credentials.access_token);
  };
  const register: AuthContextValue["register"] = async (payload) => {
    await apiFetch<User>("/auth/register", { method: "POST", body: JSON.stringify(payload) });
    await login(payload.email, payload.password, false);
  };
  const refresh = async () => { const active = tokenRef.current || await rotate(); if (active) await loadProfile(active); };
  const logout = () => {
    const active = tokenRef.current;
    clearAuth();
    if (active) void (async () => {
      try {
        const registration = await navigator.serviceWorker?.getRegistration();
        const push = await registration?.pushManager.getSubscription();
        if (push) { await apiFetch("/push/unsubscribe", { method: "POST", body: JSON.stringify({ endpoint: push.endpoint }) }, active, false); await push.unsubscribe(); }
      } catch { /* Local logout proceeds when notification service is unavailable. */ }
      try { await apiFetch("/auth/logout", { method: "POST" }, active, false); }
      catch { showToast("Signed out on this device. Server sign-out could not be confirmed while offline.", "error"); }
    })();
  };
  const access = computeAccess(user, subscription, clock);
  const value = { user, subscription, token, loading, accessLabel: access.label, hasFullAccess: access.full, login, loginWithGoogle, register, logout, refresh };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
