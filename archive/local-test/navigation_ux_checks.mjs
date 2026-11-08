// Synthetic, bounded navigation regression checks. Root runs this serially via
// run_browser.py against the existing guarded in-memory preview; no DB writes.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
const runtime = path.join(lab, 'runtime');
const recovery = path.join(root, '.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium} = await import(pathToFileURL(path.join(recovery,
  'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const origin = 'http://127.0.0.1:55446';
const browser = await chromium.launch({headless: true, args: [
  '--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run',
]});
const checks = {};
const geometry = [];
const errors = [];
let outside = 0;
let failure;
const context = await browser.newContext({serviceWorkers: 'block', hasTouch: true,
  viewport: {width: 1366, height: 900}, reducedMotion: 'reduce',
  extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++; return route.abort();
});
await context.addInitScript(() => {
  localStorage.setItem('priceyard_onboarding_seen', '1');
  localStorage.setItem('priceyard_data_saver', '1');
});
const page = await context.newPage();
page.setDefaultTimeout(10000);
page.setDefaultNavigationTimeout(12000);
page.on('pageerror', error => errors.push(error.message));
const login = async email => {
  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill(email);
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
};
const chosen = async (index, id) => {
  await page.waitForFunction(({index, id}) =>
    document.querySelectorAll('.history-filters select')[index]?.value === `id:${id}`, {index, id});
};
try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(r => r.json()));
  assert.equal(status.synthetic_only, true);
  const original = await page.evaluate(() => fetch('/api/price-updates').then(r => r.json()));
  const base = original[0];
  assert.ok(base?.commodity?.id && base?.market?.id);
  const commodity = {...base.commodity, name: base.commodity.name + ' renamed test'};
  const firstMarket = {...base.market, name: base.market.name + ' renamed test'};
  const otherMarket = {...base.market, id: 98002, name: 'Synthetic second market'};
  const otherCommodity = {...base.commodity, id: 98003, name: 'Synthetic second commodity'};
  const synthetic = (id, market = firstMarket) => ({...base, id,
    commodity, commodity_id: commodity.id, market, market_id: market.id,
    unit: '1 recorded container', bag_size: 'Recorded size', commodity_type: 'Recorded type',
    price_low: 40000 + (id % 10) * 1000, price_high: 43000 + (id % 10) * 1000,
    average_price: null, update_date_time: new Date(Date.UTC(2026, 5, 1 + id % 28, 10)).toISOString()});
  const current = [synthetic(11001), synthetic(11002, otherMarket)];
  const history = Array.from({length: 32}, (_, i) => synthetic(12000 + i));
  const queries = [];
  await page.route(url => url.origin === origin && url.pathname === '/api/commodities',
    route => route.fulfill({json: [commodity, otherCommodity]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/markets',
    route => route.fulfill({json: [firstMarket, otherMarket]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates',
    route => route.fulfill({json: current}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history/pairs',
    route => route.fulfill({json: [
      {commodity, market: firstMarket}, {commodity, market: otherMarket},
      {commodity: otherCommodity, market: otherMarket},
    ]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => {
    queries.push(new URL(route.request().url()).searchParams.toString());
    return route.fulfill({json: history});
  });
  const historyPath = market => `/history?commodity_id=${commodity.id}&market_id=${market.id}`;
  await page.goto(origin + '/prices');
  const links = page.locator('.price-option').getByRole('link', {name: 'View price history', exact: true});
  await links.nth(1).waitFor();
  assert.equal(await links.count(), 2);
  assert.equal(await links.nth(0).getAttribute('href'), historyPath(firstMarket));
  assert.equal(await links.nth(1).getAttribute('href'), historyPath(otherMarket));
  await links.nth(0).click();
  await page.waitForURL('**/history?**');
  await page.getByRole('heading', {name: 'Price history', exact: true}).waitFor();
  await page.waitForFunction(() => !document.body.innerText.includes('Checking price-history access'));
  assert.equal(await page.locator('.history-filters').count(), 0);
  assert.equal(queries.length, 0);
  checks.stable_price_history_id_links_and_guest_access_gate = true;

  await login('trial@example.com');
  await page.goto(origin + '/prices');
  await page.locator('.price-option').nth(1).getByRole('link', {name: 'View price history', exact: true}).click();
  await page.locator('.history-table-view tbody tr').nth(31).waitFor();
  await chosen(0, commodity.id); await chosen(1, otherMarket.id);
  assert.equal(await page.locator('.history-filters select').nth(0).locator('option:checked').textContent(), commodity.name);
  assert.equal(await page.locator('.history-filters select').nth(1).locator('option:checked').textContent(), otherMarket.name);
  let query = new URLSearchParams(queries.at(-1));
  assert.equal(query.get('commodity_id'), String(commodity.id));
  assert.equal(query.get('market_id'), String(otherMarket.id));
  assert.equal(query.has('commodity'), false); assert.equal(query.has('market'), false);
  checks.trial_history_preselects_renamed_records_by_exact_ids = true;

  // Exercise React Router's popstate path, not a full document reload.
  await page.evaluate(path => { history.pushState({}, '', path); window.dispatchEvent(new PopStateEvent('popstate')); }, historyPath(firstMarket));
  await chosen(1, firstMarket.id);
  await page.goBack(); await chosen(1, otherMarket.id);
  await page.goForward(); await chosen(1, firstMarket.id);
  checks.browser_back_forward_updates_history_filter_ids = true;

  await page.locator('.history-filters select').nth(1).selectOption(`id:${otherMarket.id}`);
  await page.locator('.history-filters select').nth(2).selectOption('closing');
  await page.getByRole('button', {name: 'Search history', exact: true}).click();
  await page.waitForFunction(() => !document.querySelector('.history-filters button')?.disabled);
  query = new URLSearchParams(queries.at(-1));
  assert.equal(query.get('market_id'), String(otherMarket.id)); assert.equal(query.get('time_of_day'), 'closing');
  const refreshed = page.waitForResponse(r => new URL(r.url()).pathname === '/api/auth/me');
  await page.evaluate(() => window.dispatchEvent(new Event('focus')));
  await refreshed;
  await chosen(1, otherMarket.id);
  assert.equal(await page.locator('.history-filters select').nth(2).inputValue(), 'closing');
  checks.manual_filters_survive_session_refresh = true;

  await page.evaluate(() => window.scrollTo(0, 0));
  await page.waitForFunction(() => !document.querySelector('.history-back-to-filters'));
  await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
  const back = page.getByRole('button', {name: 'Back to filters', exact: true});
  await back.waitFor({state: 'visible'});
  const fixedGeometry = await back.evaluate(node => {
    const box = node.getBoundingClientRect();
    const wa = document.querySelector('a[aria-label*="WhatsApp"], .whatsapp-float, .whatsapp-floating, .floating-whatsapp');
    const b = wa?.getBoundingClientRect();
    return {width: box.width, height: box.height, whatsAppFound: !!b, overlapsWhatsApp: !!b && box.left < b.right && box.right > b.left && box.top < b.bottom && box.bottom > b.top};
  });
  assert.ok(fixedGeometry.height >= 44); assert.equal(fixedGeometry.whatsAppFound, true); assert.equal(fixedGeometry.overlapsWhatsApp, false);
  await back.click();
  await page.waitForFunction(() => {
    const form = document.querySelector('.history-filters')?.getBoundingClientRect();
    const header = document.querySelector('.site-header')?.getBoundingClientRect();
    return form && header && form.top >= header.bottom - 2 && form.top < header.bottom + 40;
  });
  assert.equal(await page.locator('.history-filters select').first().evaluate(node => node === document.activeElement), true);
  await page.screenshot({path: path.join(runtime, 'navigation-filters-desktop.png'), fullPage: false});
  checks.back_to_filters_visibility_reduced_motion_focus_and_sticky_offset = true;

  const trialLogout = page.getByRole('button', {name: 'Log out', exact: true});
  if (!await trialLogout.isVisible()) await page.locator('.menu-button').click();
  await trialLogout.click();
  await login('admin@example.com');
  await page.goto(origin + historyPath(firstMarket));
  await page.locator('.history-filters').waitFor();
  await chosen(0, commodity.id); await chosen(1, firstMarket.id);
  checks.admin_keeps_same_direct_history_navigation = true;

  for (const width of [320, 375, 768, 1280, 1281, 1366, 1920]) {
    await page.setViewportSize({width, height: 900});
    for (const easy of [false, true]) {
      const toggle = page.getByRole('button', {name: /^Easy reading:/});
      const isOn = /On/.test(await toggle.innerText());
      if (isOn !== easy) await toggle.click();
      await page.evaluate(() => window.scrollTo(0, 0));
      const state = await page.evaluate(() => {
        const header = document.querySelector('.site-header').getBoundingClientRect();
        const controls = [...document.querySelectorAll('.display-toggles .toggle-pill')].map(node => {
          const box = node.getBoundingClientRect(); return {width: box.width, height: box.height};
        });
        const nav = document.querySelector('.main-nav');
        const navVisible = getComputedStyle(nav).display !== 'none';
        const navigationFits = !navVisible || [...nav.querySelectorAll('a, button')].every(node => {
          const box = node.getBoundingClientRect();
          return box.left >= -1 && box.right <= innerWidth + 1 && box.width >= 44 && box.height >= 44;
        });
        const brand = document.querySelector('.brand').getBoundingClientRect();
        const menu = document.querySelector('.menu-button').getBoundingClientRect();
        return {overflow: document.documentElement.scrollWidth > innerWidth + 1, headerHeight: header.height, controls,
          navigationFits, mobileBrandMenuSameRow: innerWidth > 640 || (Math.abs(brand.top - menu.top) < 12 && brand.right <= menu.left + 1)};
      });
      assert.equal(state.overflow, false, `Header overflow ${width}, easy=${easy}`);
      assert.equal(state.navigationFits, true, `Every navigation action must fit ${width}, easy=${easy}`);
      assert.equal(state.mobileBrandMenuSameRow, true);
      assert.ok(state.controls.every(box => box.height >= 44 && box.width >= 44));
      geometry.push({width, easy, ...state});
    }
    if (width === 375) await page.screenshot({path: path.join(runtime, 'navigation-header-mobile.png'), fullPage: false});
    if (width === 1366) await page.screenshot({path: path.join(runtime, 'navigation-header-desktop.png'), fullPage: false});
  }
  checks.compact_header_fits_six_widths_with_easy_reading_and_touch_controls = true;

  await page.setViewportSize({width: 375, height: 900});
  const menu = page.locator('.menu-button');
  await menu.click();
  await page.locator('.main-nav').getByRole('link', {name: 'Admin', exact: true}).waitFor({state: 'visible'});
  for (const name of ['Current Prices', 'Price History', 'Market Days', 'FAQ', 'Watchlist', 'Feedback', 'Report a price', 'Admin', 'Dashboard']) {
    assert.equal(await page.locator('.main-nav').getByRole('link', {name, exact: true}).isVisible(), true, name);
  }
  await page.keyboard.press('Escape');
  assert.equal(await menu.getAttribute('aria-expanded'), 'false');
  assert.equal(await menu.evaluate(node => node === document.activeElement), true);
  checks.mobile_menu_preserves_admin_navigation_escape_and_focus = true;

  await page.setViewportSize({width: 844, height: 390});
  await menu.click();
  const navBounds = await page.locator('.main-nav').boundingBox();
  assert.ok(navBounds && navBounds.y + navBounds.height <= 391, 'Landscape menu must fit the viewport');
  const logout = page.locator('.main-nav').getByRole('button', {name: 'Log out', exact: true});
  await logout.scrollIntoViewIfNeeded();
  const logoutBounds = await logout.boundingBox();
  assert.ok(logoutBounds && logoutBounds.y >= 0 && logoutBounds.y + logoutBounds.height <= 391,
    'Last navigation action must remain reachable in landscape');
  await page.keyboard.press('Escape');
  checks.landscape_navigation_scroll_reaches_logout_without_clipping = true;
  assert.deepEqual(errors, []); assert.equal(outside, 0);
} catch (error) {
  failure = error.stack || String(error);
  await page.screenshot({path: path.join(runtime, 'navigation-ux-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, failure,
    external_page_requests: outside, page_errors: errors, synthetic_only: true,
    production_connections: 0, database_changes: 0};
  fs.writeFileSync(path.join(runtime, 'navigation-ux-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await browser.close();
  if (failure) process.exitCode = 1;
}
