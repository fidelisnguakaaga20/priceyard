// Cache only identified public resources. Never turn an authenticated or
// historical response into offline public data on a shared device.
const CACHE_VERSION = "priceyard-v2";
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const DATA_CACHE = `${CACHE_VERSION}-data`;
const SAVED_AT_HEADER = "X-PriceYard-Saved-At";
const CACHE_HEADER = "X-PriceYard-Cache";
const APP_ORIGIN = self.location.origin;
const API_BASE = (() => {
  try {
    const value = new URL(new URL(self.location.href).searchParams.get("api") || "/api", APP_ORIGIN);
    if (value.username || value.password || value.search || value.hash) return null;
    if (value.protocol !== "https:" && !(value.protocol === "http:" && ["127.0.0.1", "localhost", "[::1]"].includes(value.hostname))) return null;
    value.pathname = value.pathname.replace(/\/+$/, "");
    return value;
  } catch { return null; }
})();

function publicApiResource(url) {
  if (!API_BASE || url.origin !== API_BASE.origin) return false;
  const prefix = API_BASE.pathname.replace(/\/+$/, "");
  if (!url.pathname.startsWith(prefix + "/")) return false;
  const endpoint = url.pathname.slice(prefix.length);
  if (endpoint === "/price-updates") {
    return [...url.searchParams.keys()].every(key => ["commodity", "market", "movement"].includes(key));
  }
  return !url.search && (/^\/(commodities|markets|faq)(\/\d+)?$/.test(endpoint) || ["/market-days", "/testimonials"].includes(endpoint));
}

function publicNavigation(url) {
  return url.origin === APP_ORIGIN && !url.search &&
    (["/", "/prices", "/market-days", "/faq"].includes(url.pathname) || url.pathname.startsWith("/commodities/"));
}

function staticAsset(url) {
  return url.origin === APP_ORIGIN && !url.search &&
    (url.pathname.startsWith("/assets/") || url.pathname.startsWith("/icons/") || url.pathname === "/manifest.json");
}

function privateResponse(response) {
  const control = response.headers.get("Cache-Control") || "";
  const vary = (response.headers.get("Vary") || "").toLowerCase().split(",").map(value => value.trim());
  return /(?:^|,)\s*(?:private|no-store)(?:\s|,|=|$)/i.test(control) || vary.some(value => ["*", "authorization", "cookie"].includes(value));
}

function cacheable(response) {
  return response.ok && !response.redirected && !["opaque", "opaqueredirect", "error"].includes(response.type) && !privateResponse(response);
}

function validSavedAt(value) {
  const parsed = Date.parse(value || "");
  return Number.isFinite(parsed) && new Date(parsed).toISOString() === value;
}

function retain(event, promise) {
  // Storage/quota failure must not turn a successful server response into an error.
  event.waitUntil(promise.catch(() => {}));
}

self.addEventListener("install", event => {
  self.skipWaiting();
  retain(event, (async () => {
    const cache = await caches.open(SHELL_CACHE);
    for (const path of ["/", "/manifest.json"]) {
      try {
        const response = await fetch(new URL(path, APP_ORIGIN).href);
        if (cacheable(response)) await cache.put(path, response);
      } catch { /* Existing network response remains authoritative. */ }
    }
  })());
});

self.addEventListener("activate", event => {
  event.waitUntil((async () => {
    // Remove only the two known unmanaged legacy stores, never other/future caches.
    const names = await caches.keys();
    await Promise.all(names.filter(name => ["priceyard-v1-shell", "priceyard-v1-data"].includes(name)).map(name => caches.delete(name)));
    await self.clients.claim();
  })());
});

self.addEventListener("fetch", event => {
  const {request} = event;
  if (request.method !== "GET" || request.headers.has("Authorization")) return;
  const url = new URL(request.url);
  if (request.mode === "navigate") {
    if (!publicNavigation(url)) return;
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (cacheable(response) && (response.headers.get("Content-Type") || "").includes("text/html")) {
          const copy = response.clone();
          retain(event, caches.open(SHELL_CACHE).then(cache => cache.put("/", copy)));
        }
        return response;
      } catch (error) {
        const cached = await (await caches.open(SHELL_CACHE)).match("/");
        if (cached) return cached;
        throw error;
      }
    })());
    return;
  }
  if (staticAsset(url)) {
    event.respondWith((async () => {
      const cached = await caches.open(SHELL_CACHE).then(cache => cache.match(request)).catch(() => undefined);
      if (cached && cacheable(cached)) return cached;
      const response = await fetch(request);
      if (cacheable(response)) {
        const copy = response.clone();
        retain(event, caches.open(SHELL_CACHE).then(cache => cache.put(request, copy)));
      }
      return response;
    })());
    return;
  }
  if (!publicApiResource(url)) return;
  event.respondWith((async () => {
    try {
      const response = await fetch(request);
      if (cacheable(response) && /application\/(?:[\w.+-]*\+)?json/i.test(response.headers.get("Content-Type") || "")) {
        const headers = new Headers(response.headers);
        headers.set(SAVED_AT_HEADER, new Date().toISOString());
        headers.delete(CACHE_HEADER);
        const copy = new Response(response.clone().body, {status:response.status, statusText:response.statusText, headers});
        retain(event, caches.open(DATA_CACHE).then(cache => cache.put(request, copy)));
      } else if ([401,403].includes(response.status) || privateResponse(response)) {
        retain(event, caches.open(DATA_CACHE).then(cache => cache.delete(request)));
      }
      return response;
    } catch (error) {
      const cached = await (await caches.open(DATA_CACHE)).match(request);
      if (!cached || !cacheable(cached) || !validSavedAt(cached.headers.get(SAVED_AT_HEADER))) throw error;
      const headers = new Headers(cached.headers);
      headers.set(CACHE_HEADER, "saved");
      return new Response(cached.body, {status:cached.status, statusText:cached.statusText, headers});
    }
  })());
});

// Watchlist price-change alerts: show a real phone/browser notification carrying the
// title/body/url the backend sent, even if PriceYard isn't open at all.
self.addEventListener("push", (event) => {
  let payload = { title: "PriceYard", body: "A watched price changed.", url: "/" };
  try {
    if (event.data) payload = { ...payload, ...event.data.json() };
  } catch {
    // malformed payload -- fall back to the generic message above rather than dropping the notification
  }
  event.waitUntil(
    self.registration.showNotification(payload.title, {
      body: payload.body,
      icon: "/icons/icon-192.png",
      badge: "/icons/icon-192.png",
      data: { url: payload.url },
    }),
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = event.notification.data && event.notification.data.url ? event.notification.data.url : "/";
  event.waitUntil(
    (async () => {
      const windows = await clients.matchAll({ type: "window", includeUncontrolled: true });
      for (const client of windows) {
        if ("focus" in client) {
          client.focus();
          if ("navigate" in client) client.navigate(url).catch(() => {});
          return;
        }
      }
      await clients.openWindow(url);
    })(),
  );
});
