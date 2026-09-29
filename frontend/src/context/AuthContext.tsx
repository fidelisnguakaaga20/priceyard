import { createContext, useCallback, useContext, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";
import { apiFetch, setUnauthorizedHandler } from "../services/api";
import { useToast } from "./ToastContext";
import type { Subscription, User } from "../types/api";

type AccessLabel = "Guest" | "Free" | "Trial" | "Active Paid" | "Admin";

type AuthContextValue = {
  user: User | null;
  subscription: Subscription | null;
  token: string | null;
  loading: boolean;
  accessLabel: AccessLabel;
  hasFullAccess: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithGoogle: (idToken: string) => Promise<void>;
  register: (payload: { full_name: string; email: string; phone?: string; password: string; referral_code?: string }) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<void>;
};

const STORAGE_KEY = "priceyard_access_token";
const AuthContext = createContext<AuthContextValue | undefined>(undefined);

function computeAccess(user: User | null, subscription: Subscription | null): { label: AccessLabel; full: boolean } {
  if (!user) return { label: "Guest", full: false };
  if (user.role === "admin") return { label: "Admin", full: true };
  if (subscription?.status === "trial") {
    const active = !subscription.trial_ends_at || new Date(subscription.trial_ends_at).getTime() > Date.now();
    return active ? { label: "Trial", full: true } : { label: "Free", full: false };
  }
  if (subscription?.status === "active" || user.role === "paid_user") return { label: "Active Paid", full: true };
  return { label: "Free", full: false };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [token, setToken] = useState<string | null>(() => localStorage.getItem(STORAGE_KEY));
  const [user, setUser] = useState<User | null>(null);
  const [subscription, setSubscription] = useState<Subscription | null>(null);
  const [loading, setLoading] = useState(Boolean(token));
  const expiredHandledRef = useRef(false);

  const clearAuth = useCallback(() => {
    localStorage.removeItem(STORAGE_KEY);
    setToken(null);
    setUser(null);
    setSubscription(null);
    setLoading(false);
  }, []);

  useEffect(() => {
    if (token) expiredHandledRef.current = false;
  }, [token]);

  useEffect(() => {
    setUnauthorizedHandler(() => {
      if (expiredHandledRef.current) return;
      expiredHandledRef.current = true;
      clearAuth();
      showToast("Your session expired — please log in again.", "error");
      navigate("/login");
    });
    return () => setUnauthorizedHandler(null);
  }, [clearAuth, navigate, showToast]);

  const refreshWithToken = useCallback(async (activeToken: string) => {
    setLoading(true);
    try {
      const currentUser = await apiFetch<User>("/auth/me", {}, activeToken);
      setUser(currentUser);
      try {
        setSubscription(await apiFetch<Subscription>(`/subscriptions/${currentUser.id}`, {}, activeToken));
      } catch {
        setSubscription(null);
      }
    } catch {
      clearAuth();
      return;
    } finally {
      setLoading(false);
    }
  }, [clearAuth]);

  useEffect(() => {
    if (token) void refreshWithToken(token);
  }, [token, refreshWithToken]);

  const login = async (email: string, password: string) => {
    const response = await apiFetch<{ access_token: string }>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password }),
    });
    localStorage.setItem(STORAGE_KEY, response.access_token);
    setToken(response.access_token);
    await refreshWithToken(response.access_token);
  };

  const loginWithGoogle = async (idToken: string) => {
    const response = await apiFetch<{ access_token: string }>("/auth/google", {
      method: "POST",
      body: JSON.stringify({ id_token: idToken }),
    });
    localStorage.setItem(STORAGE_KEY, response.access_token);
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

  const access = computeAccess(user, subscription);
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
    logout: clearAuth,
    refresh,
  }), [user, subscription, token, loading, access.label, access.full, clearAuth]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const value = useContext(AuthContext);
  if (!value) throw new Error("useAuth must be used inside AuthProvider");
  return value;
}
