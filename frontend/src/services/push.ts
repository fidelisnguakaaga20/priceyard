import { apiFetch } from "./api";

const VAPID_PUBLIC_KEY = import.meta.env.VITE_VAPID_PUBLIC_KEY as string | undefined;

function urlBase64ToUint8Array(base64: string): Uint8Array {
  const padding = "=".repeat((4 - (base64.length % 4)) % 4);
  const base64Safe = (base64 + padding).replace(/-/g, "+").replace(/_/g, "/");
  const raw = atob(base64Safe);
  return Uint8Array.from([...raw].map((char) => char.charCodeAt(0)));
}

export function pushSupported(): boolean {
  return typeof window !== "undefined" && "serviceWorker" in navigator && "PushManager" in window && Boolean(VAPID_PUBLIC_KEY);
}

export async function getExistingPushSubscription(): Promise<PushSubscription | null> {
  if (!pushSupported()) return null;
  const registration = await navigator.serviceWorker.ready;
  return registration.pushManager.getSubscription();
}

/** A browser only ever holds one push subscription per site, shared by whichever
 * account last enabled it on this device -- so "a subscription exists" alone doesn't
 * mean it belongs to the currently logged-in user. Confirms real ownership with the
 * backend before the UI claims alerts are on. */
export async function isSubscribedAsCurrentUser(token: string): Promise<boolean> {
  const subscription = await getExistingPushSubscription();
  if (!subscription) return false;
  try {
    const result = await apiFetch<{ subscribed: boolean }>(`/push/subscribed?endpoint=${encodeURIComponent(subscription.endpoint)}`, {}, token);
    return result.subscribed;
  } catch {
    return false;
  }
}

export async function enablePushAlerts(token: string): Promise<void> {
  if (!pushSupported()) throw new Error("Push notifications aren't supported on this device or browser.");

  const permission = await Notification.requestPermission();
  if (permission !== "granted") throw new Error("Notification permission wasn't granted.");

  const registration = await navigator.serviceWorker.ready;
  let subscription = await registration.pushManager.getSubscription();
  if (!subscription) {
    subscription = await registration.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY as string),
    });
  }

  const json = subscription.toJSON();
  await apiFetch(
    "/push/subscribe",
    { method: "POST", body: JSON.stringify({ endpoint: json.endpoint, keys: { p256dh: json.keys?.p256dh, auth: json.keys?.auth } }) },
    token,
  );
}

export async function disablePushAlerts(token: string): Promise<void> {
  const subscription = await getExistingPushSubscription();
  if (!subscription) return;
  const endpoint = subscription.endpoint;
  await subscription.unsubscribe();
  await apiFetch("/push/unsubscribe", { method: "POST", body: JSON.stringify({ endpoint }) }, token);
}

/** Best-effort current-device cleanup, bounded so a broken worker/provider
 * cannot indefinitely delay server logout. No VAPID setting or new permission
 * is needed to remove an already existing browser subscription. */
export async function finishLogout(token: string, isStillLoggedOut: () => boolean): Promise<boolean> {
  const controller = new AbortController();
  let current = true;
  let timer: ReturnType<typeof setTimeout> | undefined;
  const deadline = new Promise<void>((resolve) => { timer = setTimeout(resolve, 1000); });
  const cleanup = async () => {
    if (typeof navigator === "undefined" || !("serviceWorker" in navigator)) return;
    const registration = await navigator.serviceWorker.getRegistration();
    if (!current || !isStillLoggedOut() || !registration) return;
    const subscription = await registration.pushManager.getSubscription();
    if (!current || !isStillLoggedOut() || !subscription) return;
    const native = Promise.resolve().then(() => subscription.unsubscribe()).catch(() => undefined);
    const endpoint = subscription.endpoint;
    const remove = typeof endpoint === "string" && endpoint.length > 0 && endpoint.length <= 500
      ? apiFetch("/push/unsubscribe", { method: "POST", body: JSON.stringify({ endpoint }), keepalive: true, signal: controller.signal }, token).catch(() => undefined)
      : Promise.resolve();
    await Promise.all([native, remove]);
  };
  try {
    await Promise.race([cleanup().catch(() => undefined), deadline]);
  } finally {
    current = false;
    clearTimeout(timer);
    controller.abort();
    // Always attempt revocation, even if native lookup/removal fails or hangs.
    try {
      await apiFetch<void>("/auth/logout", { method: "POST", keepalive: true }, token);
      return true;
    } catch { return false; }
  }
}
