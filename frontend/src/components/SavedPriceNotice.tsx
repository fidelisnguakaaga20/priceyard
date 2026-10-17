export function SavedPriceNotice({ savedAt }: { savedAt: string | null }) {
  if (!savedAt) return null;
  return <div className="offline-banner saved-price-notice" role="status">
    Saved copy — not a live price. Saved on this device: <time dateTime={savedAt}>{new Date(savedAt).toLocaleString()}</time>.
  </div>;
}
