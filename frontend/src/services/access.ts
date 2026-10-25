import type { Subscription, User } from "../types/api";

export type AccessLabel = "Guest" | "Free" | "Trial" | "Active Paid" | "Admin" | "Owner";

export function accessExpiresAt(subscription: Subscription | null): number | null {
  if (subscription?.status === "trial") {
    const end = subscription.trial_ends_at;
    if (!end) return Number.NaN;
    // The backend treats legacy timestamps without an offset as UTC.
    return Date.parse(/(?:Z|[+-]\d{2}:\d{2})$/i.test(end) ? end : `${end}Z`);
  }
  if (subscription?.status === "active") {
    if (subscription.end_date === null) return null; // Existing indefinite grant.
    const end = subscription.end_date;
    if (!/^\d{4}-\d{2}-\d{2}$/.test(end)) return Number.NaN;
    const midnight = Date.parse(`${end}T00:00:00Z`);
    if (!Number.isFinite(midnight) || new Date(midnight).toISOString().slice(0, 10) !== end) return Number.NaN;
    // Preserve the backend's inclusive UTC end-date rule.
    return midnight + 86_400_000;
  }
  return Number.NaN;
}

export function computeAccess(user: User | null, subscription: Subscription | null): { label: AccessLabel; full: boolean } {
  if (!user) return { label: "Guest", full: false };
  if (user.role === "admin") return { label: user.is_owner === true ? "Owner" : "Admin", full: true };
  const expiry = accessExpiresAt(subscription);
  if (expiry === null || expiry > Date.now()) {
    if (subscription?.status === "trial") return { label: "Trial", full: true };
    if (subscription?.status === "active") return { label: "Active Paid", full: true };
  }
  return { label: "Free", full: false };
}
