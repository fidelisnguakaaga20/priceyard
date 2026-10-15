import { test } from "node:test";
import assert from "node:assert/strict";
import { readFileSync } from "node:fs";
import { runInNewContext } from "node:vm";

const source = readFileSync(new URL("../public/sw.js", import.meta.url), "utf8");
const origin = "http://priceyard.fixture.test";

function harness() {
  const handlers = new Map();
  const stores = new Map();
  const calls = [];
  const messages = [];
  let network = async () => { throw new Error("synthetic offline"); };
  const key = (request) => new URL(typeof request === "string" ? request : request.url, origin).href;
  const caches = {
    open: async (name) => {
      if (!stores.has(name)) stores.set(name, new Map());
      const store = stores.get(name);
      return {
        put: async (request, response) => store.set(key(request), response.clone()),
        match: async (request) => store.get(key(request))?.clone(),
        keys: async () => [...store.keys()].map((url) => new Request(url)),
        delete: async (request) => store.delete(key(request)),
      };
    },
    keys: async () => [...stores.keys()], delete: async (name) => stores.delete(name),
  };
  class RelativeRequest extends Request { constructor(input, options) { super(typeof input === "string" ? new URL(input, origin) : input, options); } }
  const self = {
    location: { origin }, addEventListener: (name, callback) => handlers.set(name, callback),
    clients: { matchAll: async () => [{ postMessage: (message) => messages.push(message) }], claim: async () => undefined },
    registration: { getNotifications: async () => [], showNotification: async () => undefined },
  };
  const contextFetch = async (request) => { calls.push(key(request)); return network(request); };
  // The exclusively fake transport is the only fetch exposed to the worker.
  runInNewContext(source, { self, caches, fetch: contextFetch, Request: RelativeRequest, Response, Headers, URL, Date, Set, Promise });
  return {
    stores, calls, messages, network: (operation) => { network = operation; },
    fetch: async (path, options = {}) => {
      let result;
      const request = new RelativeRequest(path, options);
      handlers.get("fetch")({ request, respondWith: (promise) => { result = promise; } });
      return result === undefined ? null : await result;
    },
    message: async (data) => { let work; handlers.get("message")({ data, waitUntil: (promise) => { work = promise; } }); await work; },
    install: async () => { let work; handlers.get("install")({ waitUntil: (promise) => { work = promise; } }); await work; },
  };
}
const publicResponse = () => new Response('[{"id":1}]', { headers: { "Content-Type": "application/json", "X-PriceYard-Public": "true" } });

test("protected, historical, external and unknown requests are never intercepted", async () => {
  const worker = harness();
  for (const path of ["/api/price-updates/history", "/api/price-updates/comparison", "/api/price-updates/1", "/api/price-updates?date=2026-10-14", "/api/auth/me", "https://external.fixture.test/api/price-updates"]) {
    assert.equal(await worker.fetch(path), null);
  }
  assert.equal(await worker.fetch("/api/price-updates", { headers: { Authorization: "Bearer synthetic" } }), null);
  assert.equal(worker.calls.length, 0);
});
test("public caching requires explicit response permission", async () => {
  const worker = harness();
  worker.network(async () => new Response("[]", { headers: { "Content-Type": "application/json" } }));
  assert.equal(await (await worker.fetch("/api/price-updates")).text(), "[]");
  assert.equal(worker.stores.size, 0);
});
test("backend failure falls back with visible saved timestamp", async () => {
  const worker = harness();
  worker.network(async () => publicResponse());
  await worker.fetch("/api/price-updates");
  worker.network(async () => new Response("unavailable", { status: 503 }));
  const saved = await worker.fetch("/api/price-updates");
  assert.equal(saved.headers.get("X-PriceYard-Cached"), "true");
  assert.ok(Date.parse(saved.headers.get("X-PriceYard-Cached-At")));
  assert.equal(worker.messages.at(-1).cached, true);
});
test("expired saved prices are deleted instead of replayed", async () => {
  const worker = harness();
  worker.network(async () => publicResponse());
  await worker.fetch("/api/price-updates");
  const store = worker.stores.get("priceyard-v2-public-current");
  store.set(`${origin}/api/price-updates`, new Response("[]", { headers: { "X-PriceYard-Cached-At": "2000-01-01T00:00:00Z" } }));
  worker.network(async () => new Response("unavailable", { status: 503 }));
  assert.equal((await worker.fetch("/api/price-updates")).status, 503);
  assert.equal(store.size, 0);
});
test("public cache is bounded and logout purges it", async () => {
  const worker = harness();
  worker.network(async () => publicResponse());
  for (let id = 1; id <= 35; id++) await worker.fetch(`/api/price-updates?commodity_id=${id}`);
  assert.equal(worker.stores.get("priceyard-v2-public-current").size, 30);
  await worker.message({ type: "CLEAR_USER_STATE" });
  assert.equal(worker.stores.has("priceyard-v2-public-current"), false);
});
test("only a validated root shell is stored during installation", async () => {
  const worker = harness();
  worker.network(async () => new Response("<html>Error</html>", { headers: { "Content-Type": "text/html" } }));
  await worker.install();
  assert.equal(worker.stores.size, 0);
  worker.network(async () => new Response('<html><div id="root"></div><script src="/assets/app.js"></script></html>', { headers: { "Content-Type": "text/html" } }));
  await worker.install();
  assert.equal(worker.stores.get("priceyard-v2-shell").size, 1);
});
