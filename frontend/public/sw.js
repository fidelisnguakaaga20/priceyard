// Only the public app shell, same-origin assets, and explicitly marked current
// public prices may be cached. Account/history/provider traffic is never cached.
const VERSION = "priceyard-v2";
const SHELL_CACHE = `${VERSION}-shell`;
const DATA_CACHE = `${VERSION}-public-current`;
const DATA_MAX_AGE_MS = 24 * 60 * 60 * 1000;
const MAX_DATA_ENTRIES = 30;
const MAX_SHELL_ENTRIES = 100;
const CURRENT_FILTERS = new Set(["commodity", "market", "commodity_id", "market_id", "movement"]);

function sameOrigin(url) { return url.origin === self.location.origin; }
function publicCurrent(request, url) {
  return sameOrigin(url) && url.pathname === "/api/price-updates" &&
    !request.headers.has("Authorization") &&
    [...url.searchParams.keys()].every((key) => CURRENT_FILTERS.has(key));
}
function staticAsset(url) {
  return sameOrigin(url) && (/^\/assets\/[a-zA-Z0-9_.-]+\.(js|css|woff2?)$/.test(url.pathname) ||
    /^\/icons\/[a-zA-Z0-9_.-]+\.(png|svg)$/.test(url.pathname) || url.pathname === "/manifest.json");
}
async function boundedPut(cacheName, request, response, maxEntries) {
  const cache = await caches.open(cacheName);
  await cache.put(request, response);
  const keys = await cache.keys();
  await Promise.all(keys.slice(0, Math.max(0, keys.length - maxEntries)).map((key) => cache.delete(key)));
}
async function cacheShell() {
  const response = await fetch(new Request("/", { credentials: "omit", cache: "no-cache" }));
  if (!response.ok || !response.headers.get("Content-Type")?.includes("text/html")) return;
  if (!sameOrigin(new URL(response.url || self.location.origin))) return;
  const html = await response.clone().text();
  if (!/id=["']root["']/.test(html) || !/<script\b/.test(html)) return;
  await boundedPut(SHELL_CACHE, "/", response, MAX_SHELL_ENTRIES);
}
async function reportCache(request, cachedAt, cached) {
  const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
  for (const client of windows) client.postMessage({ type: "PRICEYARD_CACHE_STATE", url: request.url, cachedAt, cached });
}
async function publicFallback(request, originalError) {
  const cache = await caches.open(DATA_CACHE);
  const response = await cache.match(request);
  const cachedAt = response?.headers.get("X-PriceYard-Cached-At");
  const savedAt = cachedAt ? Date.parse(cachedAt) : NaN;
  if (!response || !Number.isFinite(savedAt) || Date.now() - savedAt > DATA_MAX_AGE_MS || savedAt > Date.now()) {
    if (response) await cache.delete(request);
    if (originalError instanceof Response) return originalError;
    throw originalError;
  }
  const headers = new Headers(response.headers);
  headers.set("X-PriceYard-Cached", "true");
  await reportCache(request, cachedAt, true);
  return new Response(await response.arrayBuffer(), { status: response.status, headers });
}
async function currentPrices(request) {
  let response;
  try { response = await fetch(request); }
  catch (error) { return publicFallback(request, error); }
  if (response.status >= 500) return publicFallback(request, response);
  if (response.ok && response.headers.get("X-PriceYard-Public") === "true" &&
      response.headers.get("Content-Type")?.includes("application/json")) {
    const copy = response.clone();
    const headers = new Headers(copy.headers);
    const cachedAt = new Date().toISOString();
    headers.set("X-PriceYard-Cached-At", cachedAt);
    try {
      await boundedPut(DATA_CACHE, request, new Response(await copy.arrayBuffer(), { status: copy.status, headers }), MAX_DATA_ENTRIES);
    } catch { /* A working network response remains usable if storage is full. */ }
    await reportCache(request, null, false).catch(() => undefined);
  }
  return response;
}

self.addEventListener("install", (event) => {
  // Let the existing version finish its session; activate normally on next load.
  event.waitUntil(cacheShell().catch(() => undefined));
});
self.addEventListener("activate", (event) => {
  event.waitUntil((async () => {
    const names = await caches.keys();
    await Promise.all(names.filter((name) => name.startsWith("priceyard-") && name !== SHELL_CACHE && name !== DATA_CACHE).map((name) => caches.delete(name)));
    await self.clients.claim();
  })());
});
self.addEventListener("fetch", (event) => {
  const request = event.request;
  if (request.method !== "GET" || request.headers.has("Authorization")) return;
  const url = new URL(request.url);
  if (!sameOrigin(url)) return;
  if (request.mode === "navigate") {
    event.respondWith((async () => {
      try {
        const response = await fetch(request);
        if (response.status < 500) return response;
      } catch { /* Only the validated root shell is an offline fallback. */ }
      const cache = await caches.open(SHELL_CACHE);
      return await cache.match("/") || new Response("PriceYard is unavailable offline. Reconnect and retry.", { status: 503, headers: { "Content-Type": "text/plain" } });
    })());
  } else if (staticAsset(url)) {
    event.respondWith((async () => {
      let cache;
      try { cache = await caches.open(SHELL_CACHE); } catch { return fetch(request); }
      const cached = await cache.match(request);
      if (cached) return cached;
      const response = await fetch(request);
      if (response.ok && response.type !== "opaque") await boundedPut(SHELL_CACHE, request, response.clone(), MAX_SHELL_ENTRIES).catch(() => undefined);
      return response;
    })());
  } else if (publicCurrent(request, url)) event.respondWith(currentPrices(request));
});
self.addEventListener("message", (event) => {
  if (event.data?.type === "CLEAR_USER_STATE") event.waitUntil((async () => {
    await caches.delete(DATA_CACHE);
    const notifications = await self.registration.getNotifications();
    for (const notification of notifications) notification.close();
  })());
});

function safeNotificationUrl(value) {
  try {
    const url = new URL(typeof value === "string" ? value : "/", self.location.origin);
    return sameOrigin(url) ? `${url.pathname}${url.search}${url.hash}` : "/";
  } catch { return "/"; }
}
self.addEventListener("push", (event) => {
  let data = {};
  try { data = event.data?.json() || {}; } catch { /* Generic alert remains safe. */ }
  const title = typeof data.title === "string" ? data.title.slice(0, 200) : "PriceYard";
  const body = typeof data.body === "string" ? data.body.slice(0, 800) : "A watched price changed.";
  event.waitUntil(self.registration.showNotification(title, {
    body, icon: "/icons/icon-192.png", badge: "/icons/icon-192.png", data: { url: safeNotificationUrl(data.url) },
  }));
});
self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const url = safeNotificationUrl(event.notification.data?.url);
  event.waitUntil((async () => {
    const windows = await self.clients.matchAll({ type: "window", includeUncontrolled: true });
    for (const client of windows) {
      if (new URL(client.url).origin !== self.location.origin || !("focus" in client)) continue;
      await client.focus();
      if ("navigate" in client) await client.navigate(url);
      return;
    }
    await self.clients.openWindow(url);
  })());
});
