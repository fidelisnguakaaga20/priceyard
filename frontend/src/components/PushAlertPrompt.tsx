import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { disablePushAlerts, enablePushAlerts, isSubscribedAsCurrentUser, pushSupported } from "../services/push";

export function PushAlertPrompt() {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [subscribed, setSubscribed] = useState<boolean | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!pushSupported() || !token) { setSubscribed(null); return; }
    void isSubscribedAsCurrentUser(token).then(setSubscribed);
  }, [token]);

  if (!pushSupported() || !token || subscribed === null) return null;
  if (typeof Notification !== "undefined" && Notification.permission === "denied") return null;

  const enable = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await enablePushAlerts(token);
      setSubscribed(true);
      showToast("Price alerts enabled on this device.");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setBusy(false);
    }
  };

  const disable = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await disablePushAlerts(token);
      setSubscribed(false);
      showToast("Price alerts turned off on this device.");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setBusy(false);
    }
  };

  if (subscribed) {
    return (
      <div className="push-alert-banner">
        <span>✓ Instant alerts are on for this device.</span>
        <button type="button" className="text-link text-link-button" disabled={busy} onClick={() => void disable()}>Turn off</button>
      </div>
    );
  }

  return (
    <div className="push-alert-banner">
      <span>Get a phone notification the instant a watched price changes, even if PriceYard isn&rsquo;t open.</span>
      <button type="button" className="button button-small" disabled={busy} onClick={() => void enable()}>{busy ? "Enabling…" : "Enable alerts"}</button>
    </div>
  );
}
