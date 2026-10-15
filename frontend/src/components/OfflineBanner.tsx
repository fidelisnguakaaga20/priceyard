import { useEffect, useState } from "react";

export function OfflineBanner() {
  const [online, setOnline] = useState(() => (typeof navigator === "undefined" ? true : navigator.onLine));
  const [cached, setCached] = useState<Record<string, string>>({});

  useEffect(() => {
    const goOnline = () => setOnline(true);
    const goOffline = () => setOnline(false);
    window.addEventListener("online", goOnline);
    window.addEventListener("offline", goOffline);
    const cacheState = (event: MessageEvent) => {
      if (event.data?.type !== "PRICEYARD_CACHE_STATE") return;
      setCached((state) => {
        const next = { ...state };
        if (event.data.cached && event.data.cachedAt) next[event.data.url] = event.data.cachedAt;
        else delete next[event.data.url];
        return next;
      });
    };
    navigator.serviceWorker?.addEventListener("message", cacheState);
    return () => {
      window.removeEventListener("online", goOnline);
      window.removeEventListener("offline", goOffline);
      navigator.serviceWorker?.removeEventListener("message", cacheState);
    };
  }, []);

  const saved = Object.values(cached).sort()[0];
  if (online && !saved) return null;
  return (
    <div className="offline-banner" role="status">
      {saved ? <>Showing saved public prices from {new Intl.DateTimeFormat("en-NG", { dateStyle: "medium", timeStyle: "short", timeZone: "Africa/Lagos" }).format(new Date(saved))} (Nigeria time). Reconnect and refresh before relying on them.</> : <>You&rsquo;re offline. Saved public prices may be available; account and premium requests need a connection.</>}
    </div>
  );
}
