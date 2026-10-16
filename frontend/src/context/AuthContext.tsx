import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, ApiError, setUnauthorizedHandler } from "../services/api";
import { useToast } from "./ToastContext";
import type { Subscription, User } from "../types/api";
import { accessExpiresAt, computeAccess } from "../services/access";
import type { AccessLabel } from "../services/access";

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

// "Remember me" decides where the token lives: localStorage survives closing the
// browser (stays logged in up to the token's 90-day life), sessionStorage is wiped
// the moment the tab/browser closes -- the right default on a shared/public device.
function readStoredToken(): string | null {
  try {
    return localStorage.getItem(STORAGE_KEY) || sessionStorage.getItem(STORAGE_KEY);
  } catch {
    return null;
  }
}

function writeStoredToken(token: string, remember: boolean): void {
  try {
    if (remember) {
      localStorage.setItem(STORAGE_KEY, token);
      sessionStorage.removeItem(STORAGE_KEY);
    } else {
      sessionStorage.setItem(STORAGE_KEY, token);
      localStorage.removeItem(STORAGE_KEY);
    }
  } catch {
    // storage unavailable (private mode, blocked) -- auth still works for this tab via state
  }
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
  const [token, setToken] = useState<string | null>(() => readStoredToken());
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(Boolean(token));
  const expiredHandledRef = useRef(false);
  const activeTokenRef = useRef(token);
  const refreshSequence = useRef(0);
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

  const login = async (email: string, password: string, remember = true) => {
    const response = await apiFetch<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    writeStoredToken(response.access_token, remember);
    activeTokenRef.current = response.access_token;
    profileReady.current = false;
    setToken(response.access_token);
    await refreshWithToken(response.access_token);
  };

  const loginWithGoogle = async (idToken: string) => {
    const response = await apiFetch<{ access_token: string }>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });
    writeStoredToken(response.access_token, true);
    activeTokenRef.current = response.access_token;
    profileReady.current = false;
    setToken(response.access_token);
    await refreshWithToken(response.access_token);
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
      // Local logout stays immediate. Server revocation needs connectivity;
      // an old response must never change the newly cleared account state.
      void apiFetch<void>("/auth/logout", { method: "POST", keepalive: true }, currentToken).catch(() => undefined);
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
