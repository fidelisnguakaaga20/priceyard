// Browser workflow checks: every page request is fulfilled locally or rejected.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const snapshot = process.argv[2];
const { chromium } = await import(pathToFileURL(path.join(snapshot, 'node_modules/playwright/index.mjs')));
const origin = 'http://127.0.0.1:55440';
const artifacts = path.resolve(snapshot, '../../artifacts');
await fs.mkdir(artifacts, { recursive: true });
const now = new Date().toISOString();
const commodity = { id: 1, name: 'Synthetic maize', description: 'Synthetic observation', image_url: null, is_active: true, is_upcoming: false, expected_available_date: null, created_at: now, updated_at: now };
const market = { id: 1, name: 'Synthetic market', state: 'Niger', country: 'Nigeria', market_day: null, description: null, image_url: null, is_active: true, created_at: now, updated_at: now };
const observation = { id: 1, commodity_id: 1, market_id: 1, commodity, market, price_low: '10000', price_high: '12000', average_price: null, previous_price_low: null, previous_price_high: null, unit: '1 bag', bag_size: '50kg', commodity_type: null, grade: 'A', market_day: null, time_of_day: null, movement: 'unknown', confidence_level: 'Admin confirmed', source_type: null, update_date_time: now, is_outdated: false, status: 'approved', created_at: now, updated_at: now };
let passed = 0;
const browser = await chromium.launch({ headless: true,
  args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run', '--disable-domain-reliability'] });

async function fixture({ role = 'free_user', profileFailure = false, priceFailure = false, tour = false, paymentConfirmed = false } = {}) {
  const context = await browser.newContext({ serviceWorkers: 'block', viewport: { width: 375, height: 812 } });
  const attemptedExternal = [];
  const calls = [];
  await context.routeWebSocket('**/*', (socket) => socket.close());
  await context.route('**/*', async (route) => {
    const request = route.request();
    const url = new URL(request.url());
    if (url.origin !== origin) { attemptedExternal.push(url.origin); await route.abort('blockedbyclient'); return; }
    if (url.pathname.startsWith('/api/')) {
      const endpoint = url.pathname.slice(4);
      calls.push({ endpoint, body: request.postDataJSON(), query: url.search });
      let data = [];
      let status = 200;
      if (endpoint === '/auth/login' || endpoint === '/auth/refresh') data = { access_token: 'synthetic-access', refresh_token: 'synthetic-refresh', expires_in: 900, session_expires_at: new Date(Date.now() + 86400000).toISOString() };
      else if (endpoint === '/auth/me') { status = profileFailure ? 503 : 200; data = profileFailure ? { detail: 'Synthetic account outage' } : { id: 1, full_name: 'Synthetic member', email: 'member@fixture.test', role, is_active: true, email_verified: true, referred_by_id: null, created_at: now }; }
      else if (endpoint === '/subscriptions/1') data = { id: 1, user_id: 1, status: 'trial', plan_name: 'trial', trial_started_at: now, trial_ends_at: new Date(Date.now() + 14 * 86400000).toISOString(), start_date: null, end_date: null, paid_expires_at: null, manual_grant: false, created_at: now, updated_at: now };
      else if (endpoint === '/commodities') data = [commodity];
      else if (endpoint === '/markets') data = [market];
      else if (endpoint === '/price-updates') {
        if (request.method() === 'POST') { data = { ...observation, ...request.postDataJSON(), status: 'pending' }; status = 201; }
        else { status = priceFailure ? 503 : 200; data = priceFailure ? { detail: 'Synthetic price outage' } : [observation]; }
      }
      else if (endpoint === '/price-updates/my-stats') data = { submitted: 0, pending: 0, approved: 0, rejected: 0 };
      else if (endpoint === '/auth/referral-summary') data = { referral_code: 'SYNTHETIC', referred_count: 0, reward_days: 7 };
      else if (endpoint === '/activity/summary') data = { unseen_count: 0, recent: [] };
      else if (endpoint === '/users') data = url.searchParams.get('page') === '2'
        ? [{ id: 101, full_name: 'Older synthetic member', email: 'older@fixture.test', phone: null, role: 'free_user', is_active: true, referred_by_id: null, created_at: now }]
        : Array.from({ length: 100 }, (_, index) => ({ id: index + 1, full_name: `Synthetic listed member ${index + 1}`, email: `member${index + 1}@fixture.test`, phone: null, role: 'free_user', is_active: true, referred_by_id: null, created_at: now }));
      else if (endpoint.startsWith('/payments/status/')) data = { status: paymentConfirmed ? 'success' : 'pending', access_applied: paymentConfirmed, requires_reconciliation: false };
      else if (endpoint === '/activity/ping') { status = 204; data = null; }
      await route.fulfill({ status, contentType: 'application/json', body: status === 204 ? undefined : JSON.stringify(data) });
      return;
    }
    const relative = decodeURIComponent(url.pathname).replace(/^\/+/, '');
    const candidate = path.resolve(snapshot, 'dist', relative || 'index.html');
    const root = path.resolve(snapshot, 'dist');
    if (!candidate.startsWith(root + path.sep) && candidate !== path.join(root, 'index.html')) { await route.abort(); return; }
    let file = candidate;
    try { if (!(await fs.stat(file)).isFile()) file = path.join(root, 'index.html'); } catch { file = path.join(root, 'index.html'); }
    const type = file.endsWith('.js') ? 'application/javascript' : file.endsWith('.css') ? 'text/css' : file.endsWith('.svg') ? 'image/svg+xml' : file.endsWith('.png') ? 'image/png' : 'text/html';
    await route.fulfill({ contentType: type, body: await fs.readFile(file) });
  });
  if (!tour) await context.addInitScript(() => localStorage.setItem('priceyard_onboarding_seen', '1'));
  const page = await context.newPage();
  page.setDefaultTimeout(10000);
  const errors = [];
  page.on('pageerror', (error) => errors.push(error.message));
  return { context, page, calls, errors, attemptedExternal };
}
async function check(name, options, run) {
  const item = await fixture(options);
  try { await run(item); assert.deepEqual(item.errors, []); assert.deepEqual(item.attemptedExternal, []); passed++; console.log('PASS ' + name); }
  finally { await item.context.close(); }
}
async function login(page) {
  await page.goto(origin + '/login');
  await page.getByLabel('Email', { exact: true }).fill('member@fixture.test');
  await page.getByLabel('Password', { exact: true }).fill('SyntheticPass8');
  await page.getByRole('button', { name: 'Log in', exact: true }).click();
}
try {
  await check('guest prices finish loading and preserve measurements', {}, async ({ page }) => {
    await page.goto(origin + '/prices');
    await page.getByRole('heading', { name: 'Synthetic maize' }).waitFor();
    assert.match(await page.locator('main').innerText(), /50kg/);
    assert.match(await page.locator('main').innerText(), /Grade: A/);
    await page.screenshot({ path: path.join(artifacts, 'prices-mobile-synthetic.png'), fullPage: true });
    await page.getByLabel('Commodity', { exact: false }).selectOption('1');
    await page.getByRole('button', { name: 'Apply', exact: true }).click();
    await page.waitForURL('**/prices?commodity_id=1');
  });
  await check('mobile menu closes with Escape and restores keyboard focus', {}, async ({ page }) => {
    await page.goto(origin + '/prices');
    const menu = page.getByRole('button', { name: 'Toggle navigation' });
    await menu.click();
    assert.equal(await menu.getAttribute('aria-expanded'), 'true');
    await page.keyboard.press('Escape');
    assert.equal(await menu.getAttribute('aria-expanded'), 'false');
    assert.equal(await menu.evaluate((element) => element === document.activeElement), true);
    for (const width of [320, 375, 768]) {
      await page.setViewportSize({ width, height: 812 });
      assert.ok(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), 'horizontal page overflow at ' + width);
    }
  });
  await check('onboarding traps focus and Escape dismisses it', { tour: true }, async ({ page }) => {
    await page.goto(origin + '/prices');
    const dialog = page.getByRole('dialog', { name: 'Welcome to PriceYard' });
    await dialog.waitFor();
    for (let index = 0; index < 5; index++) { await page.keyboard.press('Tab'); assert.ok(await dialog.evaluate((element) => element.contains(document.activeElement))); }
    await page.keyboard.press('Escape');
    await dialog.waitFor({ state: 'hidden' });
  });
  await check('price outage replaces loading with a usable retry', { priceFailure: true }, async ({ page }) => {
    await page.goto(origin + '/prices');
    await page.getByRole('button', { name: 'Retry', exact: true }).waitFor();
    assert.equal(await page.getByText('Loading approved prices…', { exact: true }).count(), 0);
  });
  await check('successful login shows the approved fixed-duration plans', {}, async ({ page }) => {
    await login(page);
    await page.waitForURL('**/dashboard');
    await page.getByRole('button', { name: '₦2,500 / 30 days', exact: true }).waitFor();
    await page.getByRole('button', { name: '₦6,000 / 90 days', exact: true }).waitFor();
  });
  await check('account outage never reports a successful login', { profileFailure: true }, async ({ page }) => {
    await login(page);
    await page.getByText('Synthetic account outage', { exact: true }).waitFor();
    assert.ok(page.url().endsWith('/login'));
    assert.equal(await page.getByText('Login successful. Welcome back to PriceYard.', { exact: true }).count(), 0);
  });
  await check('pending payment never claims activation', {}, async ({ page }) => {
    await login(page); await page.waitForURL('**/dashboard');
    await page.goto(origin + '/payment/callback?reference=py_synthetic');
    await page.getByRole('heading', { name: 'Payment status', exact: true }).waitFor();
    assert.equal(await page.getByRole('heading', { name: 'Access activated' }).count(), 0);
  });
  await check('confirmed payment displays activation only after server status', { paymentConfirmed: true }, async ({ page }) => {
    await login(page); await page.waitForURL('**/dashboard');
    await page.goto(origin + '/payment/callback?reference=py_synthetic');
    await page.getByRole('heading', { name: 'Access activated', exact: true }).waitFor();
  });
  await check('reporter submits Lagos timestamp without inventing an average', { role: 'reporter' }, async ({ page, calls }) => {
    await login(page); await page.waitForURL('**/dashboard');
    await page.goto(origin + '/report-price');
    await page.getByLabel('Commodity', { exact: false }).selectOption('1');
    await page.getByLabel('Market', { exact: false }).selectOption('1');
    await page.getByLabel('Price low', { exact: true }).fill('10000');
    await page.getByLabel('Price high', { exact: true }).fill('12000');
    await page.locator('[name=bag_size]').fill('50kg');
    await page.locator('[name=update_date_time]').fill('2026-10-14T13:30');
    await page.getByRole('button', { name: 'Submit price report', exact: true }).click();
    await page.getByText('Thank you. Your price report was submitted for review.', { exact: true }).waitFor();
    const submitted = calls.find((call) => call.endpoint === '/price-updates' && call.body?.price_low === 10000).body;
    assert.equal(submitted.average_price, null);
    assert.equal(submitted.update_date_time, '2026-10-14T12:30:00.000Z');
  });
  await check('administrator can reach older records beyond the first hundred', { role: 'admin' }, async ({ page, calls }) => {
    await login(page); await page.waitForURL('**/dashboard');
    await page.goto(origin + '/admin/users');
    await page.getByText('Synthetic listed member 100', { exact: true }).filter({ visible: true }).waitFor();
    await page.getByRole('button', { name: 'Next page', exact: true }).click();
    await page.getByText('Older synthetic member', { exact: true }).filter({ visible: true }).waitFor();
    assert.ok(calls.some((call) => call.endpoint === '/users' && new URLSearchParams(call.query).get('page') === '2'));
    await page.getByRole('button', { name: 'Previous page', exact: true }).click();
    await page.getByText('Synthetic listed member 100', { exact: true }).filter({ visible: true }).waitFor();
  });
  const result = { browser_checks_passed: passed, live_requests: 0, boundary: 'fresh Chromium profile; all page requests fulfilled locally; service workers blocked' };
  await fs.writeFile(path.join(artifacts, 'browser-checks.json'), JSON.stringify(result, null, 2));
  console.log(JSON.stringify(result));
} finally { await browser.close(); }
