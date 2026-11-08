import { useState } from "react";
import type { ShareContent } from "../utils";

/** navigator.share opens the device's native share sheet (WhatsApp, Facebook, Telegram,
 * SMS, etc. -- whatever's installed), so one button covers every platform instead of
 * maintaining a separate link per app. Not supported on some desktop browsers. */
function canUseNativeShare(): boolean {
  return typeof navigator !== "undefined" && typeof navigator.share === "function";
}

function useNativeShare(content: ShareContent) {
  const [busy, setBusy] = useState(false);
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
  return { busy, share };
}

export function NativeShareButton({ content, label = "Share" }: { content: ShareContent; label?: string }) {
  const { busy, share } = useNativeShare(content);
  if (!canUseNativeShare()) return null;

  // Muted styling: a secondary, catch-all option on cards that have their own main action.
  return (
    <button
      type="button"
      className="text-link-button muted share-more-button"
      disabled={busy}
      onClick={() => void share()}
    >
      {busy ? "Sharing…" : `📤 ${label}`}
    </button>
  );
}

/** The single Share action on a price: opens the device's share sheet where the browser
 * has one, and otherwise opens WhatsApp with the same message ready, so every visitor
 * can still share. */
export function PriceShareButton({ content, whatsAppUrl }: { content: ShareContent; whatsAppUrl: string }) {
  const { busy, share } = useNativeShare(content);
  if (!canUseNativeShare()) {
    return (
      <a className="text-link" href={whatsAppUrl} target="_blank" rel="noopener noreferrer">
        📤 Share
      </a>
    );
  }
  return (
    <button
      type="button"
      className="text-link text-link-button share-button"
      disabled={busy}
      onClick={() => void share()}
    >
      {busy ? "Sharing…" : "📤 Share"}
    </button>
  );
}
