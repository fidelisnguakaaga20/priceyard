import { useState } from "react";
import type { ShareContent } from "../utils";

/** navigator.share opens the device's native share sheet (WhatsApp, Facebook, Telegram,
 * SMS, etc. -- whatever's installed), so one button covers every platform instead of
 * maintaining a separate link per app. Not supported on most desktop browsers, where
 * the WhatsApp link next to it remains the primary share path. */
function canUseNativeShare(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

export function NativeShareButton({ content, label = "Share" }: { content: ShareContent; label?: string }) {
  const [busy, setBusy] = useState(false);
  if (!canUseNativeShare()) return null;

  const share = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await navigator.share({ text: content.message, url: content.url });
    } catch {
      // user cancelled the share sheet or it failed silently -- nothing to show for either
    } finally {
      setBusy(false);
    }
  };

  return (
    <button type="button" className="text-link text-link-button" disabled={busy} onClick={() => void share()}>
      {busy ? "Sharing…" : `${label} elsewhere →`}
    </button>
  );
}
