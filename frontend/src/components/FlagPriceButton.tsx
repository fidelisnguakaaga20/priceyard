import { useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";

export function FlagPriceButton({ priceUpdateId }: { priceUpdateId: number }) {
  const { token } = useAuth();
  const { showToast } = useToast();
  const [flagged, setFlagged] = useState(false);
  const [busy, setBusy] = useState(false);

  if (!token) return null;

  const flag = async () => {
    if (busy || flagged) return;
    setBusy(true);
    try {
      await apiFetch(`/price-updates/${priceUpdateId}/flag`, { method: "POST", body: JSON.stringify({}) }, token);
      setFlagged(true);
      showToast("Thanks — we'll check this price.");
    } catch (err) {
      showToast((err as Error).message, "error");
    } finally {
      setBusy(false);
    }
  };

  return (
    <button type="button" className="text-link-button muted" disabled={busy || flagged} onClick={() => void flag()}>
      {flagged ? "🚩 Reported" : "🚩 Report wrong price"}
    </button>
  );
}
