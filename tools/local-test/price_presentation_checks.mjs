// Focused UI regressions only: the existing guarded, in-memory preview and
// synthetic HTTP responses. No production data, credentials or provider calls.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
const recovery = path.join(root, '.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium} = await import(pathToFileURL(path.join(recovery, 'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const origin = 'http://127.0.0.1:55446';
const browser = await chromium.launch({headless: true, args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run']});
const context = await browser.newContext({serviceWorkers: 'block', viewport: {width: 1366, height: 900}, extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
let outside = 0;
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++; return route.abort();
});
await context.addInitScript(() => { localStorage.setItem('priceyard_onboarding_seen', '1'); localStorage.setItem('priceyard_data_saver', '1'); });
const page = await context.newPage();
page.setDefaultTimeout(12000); page.setDefaultNavigationTimeout(12000);
const errors = []; page.on('pageerror', error => errors.push(error.message));
const checks = {};
try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(r => r.json()));
  assert.equal(status.synthetic_only, true);
  const original = await page.evaluate(() => fetch('/api/price-updates').then(r => r.json()));
  const base = original[0]; assert.ok(base);
  const price = (id, changes = {}) => ({...base, id, price_low: 40000, price_high: 43000, average_price: null,
    update_date_time: `2026-06-${String(id % 20 + 1).padStart(2, '0')}T10:00:00Z`,
    unit: '1 container', bag_size: 'Recorded size one', commodity_type: 'Recorded type', ...changes});
  const current = [price(101), price(102, {bag_size: 'Recorded size two', price_low: 41000, price_high: 44000}),
    price(103, {market_id: 9002, market: {...base.market, id: 9002, name: 'Synthetic second market'}})];
  let shownCurrent = current;
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates', route => route.fulfill({json: shownCurrent}));
  await page.goto(origin + '/prices');
  await page.locator('.commodity-price-card').waitFor();
  assert.equal(await page.locator('.commodity-price-card').count(), 1);
  assert.equal(await page.locator('.commodity-price-card .commodity-image').count(), 1);
  assert.equal(await page.locator('.price-option').count(), 3);
  for (const option of await page.locator('.price-option').all()) {
    assert.equal(await option.getByRole('link', {name: 'Share on WhatsApp', exact: true}).count(), 1);
    assert.equal(await option.getByRole('link', {name: /See what this price means/}).count(), 1);
    assert.equal(await option.getByRole('link', {name: /Log in to watch/}).count(), 1);
  }
  assert.match(await page.locator('.price-option').nth(0).innerText(), /Recorded size one/);
  assert.match(await page.locator('.price-option').nth(1).innerText(), /Recorded size two/);
  assert.match(await page.locator('.price-option').nth(2).innerText(), /Synthetic second market/);
  checks.one_photo_all_distinct_records_and_guest_actions = true;
  // Same commodity name with a different ID must never be collapsed.
  shownCurrent = [...current, price(104, {commodity_id: 9003, commodity: {...base.commodity, id: 9003}})];
  await page.reload(); await page.locator('.price-option').nth(3).waitFor();
  assert.equal(await page.locator('.commodity-price-card').count(), 2);
  checks.commodity_ids_not_names_control_grouping = true;
  await page.locator('.filter-bar select').nth(0).selectOption({label: base.commodity.name});
  shownCurrent = [current[1]];
  await page.getByRole('button', {name: 'Apply', exact: true}).click();
  await page.waitForFunction(() => document.querySelectorAll('.price-option').length === 1);
  assert.match(await page.locator('.price-option').innerText(), /Recorded size two/);
  checks.filters_replace_grouped_results = true;
  shownCurrent = current;
  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('trial@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  await page.goto(origin + '/prices'); await page.locator('.price-option').nth(2).waitFor();
  let watchedBody;
  await page.route(origin + '/api/watchlist', async route => {
    watchedBody = route.request().postDataJSON();
    await route.fulfill({status: 201, json: {id: 1}});
  });
  await page.locator('.price-option').nth(2).getByRole('button', {name: /Watch this/}).click();
  await page.locator('.price-option').nth(2).getByRole('button', {name: /Watching/}).waitFor();
  assert.deepEqual(watchedBody, {commodity_id: base.commodity_id, market_id: 9002});
  checks.watch_action_preserves_record_identity = true;
  // Complete pairs, a different size, and old records lacking specifications.
  let history = [price(201), price(202, {price_low: 45000, price_high: 48000}),
    price(203, {bag_size: 'Recorded size two'}), price(204, {bag_size: 'Recorded size two'}),
    price(205, {bag_size: null, commodity_type: null}), price(206, {bag_size: null, commodity_type: null})];
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => route.fulfill({json: history}));
  await page.goto(origin + '/history');
  await page.locator('.history-table-view tbody tr').nth(5).waitFor();
  assert.equal(await page.locator('.trend-chart').count(), 3);
  assert.equal(await page.locator('.trend-line').count(), 2);
  assert.equal(await page.locator('.trend-dot').count(), 6);
  assert.equal(await page.locator('.trend-range').count(), 6);
  const legacy = page.locator('.history-price-series').filter({hasText: 'Size not recorded'});
  assert.equal(await legacy.locator('.trend-line').count(), 0);
  assert.equal(await legacy.locator('.trend-dot').count(), 2);
  await legacy.getByText(/points are not joined/).waitFor();
  assert.equal(await page.getByRole('img', {name: /Price trend over time/}).count(), 2);
  checks.matching_lines_separate_sizes_legacy_points_and_history_preserved = true;
  // One saved record remains visible, and zero prices/flat series are valid.
  history = [price(207, {price_low: 0, price_high: 0})];
  await page.reload(); await page.locator('.history-table-view tbody tr').waitFor();
  assert.equal(await page.locator('.trend-chart').count(), 1);
  assert.equal(await page.locator('.trend-line').count(), 0);
  assert.equal(await page.locator('.trend-dot').count(), 1);
  assert.equal(await page.locator('svg .trend-dot').getAttribute('cx'), '320');
  assert.equal(await page.locator('svg .trend-dot').getAttribute('cy'), '90');
  checks.single_flat_zero_price_is_visible = true;
  history = [price(208, {update_date_time: '2026-06-01T12:00:00'}), price(209, {price_high: -1}),
    price(210, {average_price: 999999}), price(211)];
  await page.reload(); await page.locator('.history-table-view tbody tr').nth(3).waitFor();
  assert.equal(await page.locator('.trend-dot').count(), 1);
  assert.equal(await page.locator('.history-table-view tbody tr').count(), 4);
  await page.getByText(/They remain in the history below/).waitFor();
  checks.invalid_prices_and_ambiguous_times_not_plotted_but_retained = true;
  history = [price(201), price(202), price(205, {bag_size: null, commodity_type: null})];
  const geometry = [];
  for (const width of [375, 1366]) for (const theme of ['dark', 'light']) {
    await page.setViewportSize({width, height: 900});
    await page.evaluate(theme => { localStorage.setItem('priceyard_dark_mode', theme === 'dark' ? '1' : '0');
      localStorage.setItem('priceyard_easy_reading', '1'); }, theme);
    await page.goto(origin + '/prices'); await page.locator('.price-option').nth(2).waitFor();
    assert.equal(await page.locator('.commodity-price-card .commodity-image').count(), 1);
    const cardsFit = await page.locator('.price-option').evaluateAll(nodes => nodes.every(node => node.scrollWidth <= node.clientWidth + 1));
    assert.equal(cardsFit, true, 'Grouped price contents must fit');
    await page.goto(origin + '/history'); await page.locator('.trend-chart').nth(1).waitFor();
    await page.evaluate(theme => document.documentElement.dataset.theme = theme, theme);
    const state = await page.locator('.trend-line').evaluate(node => ({stroke: getComputedStyle(node).stroke,
      color: getComputedStyle(document.documentElement).getPropertyValue('--color-link').trim(),
      overflow: document.documentElement.scrollWidth > innerWidth}));
    assert.equal(state.overflow, false);
    assert.ok(state.stroke !== 'rgb(0, 0, 0)' && state.stroke !== 'none');
    geometry.push({width, theme, stroke: state.stroke});
    if (width === 375 && theme === 'dark') await page.screenshot({path: path.join(lab, 'runtime/price-history-restored-mobile.png'), fullPage: true});
  }
  checks.mobile_easy_reading_and_theme_compatible_graphs = true;
  await page.setViewportSize({width: 1366, height: 900});
  await page.goto(origin + '/prices'); await page.locator('.price-option').nth(2).waitFor();
  await page.screenshot({path: path.join(lab, 'runtime/grouped-commodity-prices.png'), fullPage: true});
  await page.goto(origin + '/history'); await page.locator('.trend-chart').nth(1).waitFor();
  await page.screenshot({path: path.join(lab, 'runtime/price-history-restored.png'), fullPage: true});
  assert.equal(outside, 0); assert.deepEqual(errors, []);
  const report = {passed: Object.keys(checks).length, checks, geometry, external_page_requests: outside, production_connections: 0,
    synthetic_only: true, database_changes: 0};
  fs.writeFileSync(path.join(lab, 'runtime/price-presentation-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
} finally { await browser.close(); }
