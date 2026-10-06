// Minimal offline support: cache the app shell and public GET data as they're used,
// so a trader with no signal still sees the last prices this device already loaded,
// instead of a blank page. Never touches non-GET requests or anything carrying an
// Authorization header -- personalized/write requests always go straight to the network.
const CACHE_VERSION = "priceyard-v1";
const SHELL_CACHE = `${CACHE_VERSION}-shell`;
const DATA_CACHE = `${CACHE_VERSION}-data`;

self.addEventListener("install", (event) => {
  self.skipWaiting();
  event.waitUntil(
    caches.open(SHELL_CACHE).then((cache) => cache.addAll(["/", "/manifest.json"]).catch(() => {})),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    (async () => {
      const names = await caches.keys();
      await Promise.all(
        names
          .filter((name) => name.startsWith("priceyard-") && !name.startsWith(CACHE_VERSION))
          .map((name) => caches.delete(name)),
      );
      await self.clients.claim();
    })(),
  );
});

function isStaticAsset(url) {
  return url.pathname.startsWith("/assets/") || url.pathname.startsWith("/icons/") || url.pathname === "/manifest.json";
}

self.addEventListener("fetch", (event) => {
  const { request } = event;
  if (request.method !== "GET") return; // never intercept writes -- they must fail normally if offline

  const url = new URL(request.url);

  // Full page loads (typing the URL, refreshing, opening from the home screen icon):
  // try the network for the freshest shell, fall back to the last cached one if offline.
  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then((response) => {
          caches.open(SHELL_CACHE).then((cache) => cache.put("/", response.clone())).catch(() => {});
          return response;
        })
        .catch(() => caches.match("/")),
    );
    return;
  }

  // Hashed JS/CSS bundles and icons never change content under the same filename,
  // so once cached they can be served straight from cache.
  if (isStaticAsset(url)) {
    event.respondWith(
      caches.match(request).then(
        (cached) =>
          cached ||
          fetch(request).then((response) => {
            caches.open(SHELL_CACHE).then((cache) => cache.put(request, response.clone())).catch(() => {});
            return response;
          }),
      ),
    );
    return;
  }

  // Everything else GET (price-updates, commodities, markets, FAQ, ...) is API data:
  // prefer the network for current prices, but fall back to the last cached response
  // when offline. Skipped for requests carrying a login token, since those return
  // personalized data that must never be replayed stale from a shared device's cache.
  if (!request.headers.has("Authorization")) {
    event.respondWith(
      fetch(request)
        .then((response) => {
          if (response.ok) {
            const copy = response.clone();
            caches.open(DATA_CACHE).then((cache) => cache.put(request, copy)).catch(() => {});
          }
          return response;
        })
        .catch(() => caches.match(request).then((cached) => cached || Promise.reject(new Error("offline, nothing cached yet")))),
    );
  }
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
