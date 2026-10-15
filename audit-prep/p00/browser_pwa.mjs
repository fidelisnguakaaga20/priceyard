// Actual service-worker lifecycle with a synthetic-only literal loopback server.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import http from 'node:http';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const snapshot = process.argv[2];
const root = path.resolve(snapshot, 'dist');
const origin = 'http://127.0.0.1:55441';
const { chromium } = await import(pathToFileURL(path.join(snapshot, 'node_modules/playwright/index.mjs')));
const now = new Date().toISOString();
const commodity = { id: 1, name: 'PWA synthetic maize', image_url: null, is_active: true, is_upcoming: false };
const market = { id: 1, name: 'PWA synthetic market', state: 'Niger', is_active: true };
const price = { id: 1, commodity_id: 1, market_id: 1, commodity, market, price_low: '100', price_high: '120', average_price: null,
  previous_price_low: null, previous_price_high: null, unit: '1 bag', bag_size: '50kg', grade: 'A', movement: 'unknown',
  confidence_level: 'Admin confirmed', update_date_time: now, created_at: now, updated_at: now, status: 'approved', is_outdated: false };
const server = http.createServer(async (request, response) => {
  try {
    const url = new URL(request.url, origin);
    if (url.pathname.startsWith('/api/')) {
      if (url.pathname === '/api/activity/ping') { response.writeHead(204).end(); return; }
      response.setHeader('Content-Type', 'application/json');
      if (url.pathname === '/api/price-updates' && !request.headers.authorization) response.setHeader('X-PriceYard-Public', 'true');
      const data = url.pathname === '/api/commodities' ? [commodity] : url.pathname === '/api/markets' ? [market]
        : url.pathname.startsWith('/api/price-updates') ? [price] : [];
      response.end(JSON.stringify(data)); return;
    }
    const candidate = path.resolve(root, decodeURIComponent(url.pathname).replace(/^\/+/, '') || 'index.html');
    if (!candidate.startsWith(root + path.sep)) { response.writeHead(400).end(); return; }
    let file = candidate;
    try { if (!(await fs.stat(file)).isFile()) file = path.join(root, 'index.html'); } catch { file = path.join(root, 'index.html'); }
    const type = file.endsWith('.js') ? 'application/javascript' : file.endsWith('.css') ? 'text/css' : file.endsWith('.json') ? 'application/json' : file.endsWith('.png') ? 'image/png' : file.endsWith('.svg') ? 'image/svg+xml' : 'text/html';
    response.setHeader('Content-Type', type);
    response.end(await fs.readFile(file));
  } catch { response.writeHead(500).end(); }
});
await new Promise((resolve, reject) => { server.once('error', reject); server.listen(55441, '127.0.0.1', resolve); });
let browser;
try {
  browser = await chromium.launch({ headless: true, args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run'] });
  const context = await browser.newContext({ serviceWorkers: 'allow' });
  const external = [];
  await context.routeWebSocket('**/*', (socket) => socket.close());
  await context.route('**/*', async (route) => {
    if (new URL(route.request().url()).origin === origin) await route.continue();
    else { external.push(new URL(route.request().url()).origin); await route.abort('blockedbyclient'); }
  });
  await context.addInitScript(() => localStorage.setItem('priceyard_onboarding_seen', '1'));
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  await page.goto(origin + '/prices');
  await page.getByRole('heading', { name: commodity.name }).waitFor();
  await page.evaluate(async () => { await navigator.serviceWorker.ready; });
  await page.waitForFunction(() => Boolean(navigator.serviceWorker.controller));
  // Reload once under worker control so hashed JS/CSS can be captured.
  await page.reload();
  await page.getByRole('heading', { name: commodity.name }).waitFor();
  await page.evaluate(async () => {
    await fetch('/api/price-updates');
    await fetch('/api/price-updates', { headers: { Authorization: 'Bearer synthetic-never-valid' } });
    await fetch('/api/price-updates/history');
  });
  const cachedRequests = await page.evaluate(async () => (await Promise.all((await caches.keys()).map(async (name) => (await (await caches.open(name)).keys()).map((request) => request.url)))).flat());
  assert.ok(cachedRequests.includes(origin + '/api/price-updates'));
  assert.ok(!cachedRequests.some((url) => url.includes('/history')));
  // Close the synthetic server as well: browser offline emulation alone may
  // leave worker network contexts online in some Chromium/Playwright versions.
  server.closeAllConnections();
  await new Promise((resolve) => server.close(resolve));
  await context.setOffline(true);
  const saved = await page.evaluate(async () => {
    const response = await fetch('/api/price-updates');
    let historyBlocked = false;
    let authenticatedBlocked = false;
    try { await fetch('/api/price-updates/history'); } catch { historyBlocked = true; }
    try { await fetch('/api/price-updates', { headers: { Authorization: 'Bearer synthetic-never-valid' } }); } catch { authenticatedBlocked = true; }
    return { cached: response.headers.get('X-PriceYard-Cached'), cachedAt: response.headers.get('X-PriceYard-Cached-At'), rows: await response.json(), historyBlocked, authenticatedBlocked };
  });
  assert.equal(saved.cached, 'true'); assert.ok(Date.parse(saved.cachedAt)); assert.equal(saved.rows[0].id, 1);
  assert.equal(saved.historyBlocked, true); assert.equal(saved.authenticatedBlocked, true);
  await page.reload();
  await page.getByRole('heading', { name: commodity.name }).waitFor();
  await page.evaluate(() => navigator.serviceWorker.controller.postMessage({ type: 'CLEAR_USER_STATE' }));
  await page.waitForFunction(async () => !(await caches.keys()).some((name) => name.endsWith('-public-current')));
  assert.deepEqual(external, []);
  const result = { pwa_checks_passed: 1, scope: 'actual worker registration, public cache, offline shell/assets/prices, protected/history cache exclusion and logout purge', external_page_requests: 0 };
  const artifacts = path.resolve(snapshot, '../../artifacts');
  await fs.writeFile(path.join(artifacts, 'pwa-checks.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result));
} finally {
  if (browser) await browser.close();
  server.closeAllConnections();
  await new Promise((resolve) => server.close(resolve));
}
