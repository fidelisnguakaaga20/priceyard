// Bounded synthetic UI regressions for graph discovery, compact ticker and
// movement-error recovery. Run only through the existing guarded preview.
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
const context = await browser.newContext({serviceWorkers: 'block', hasTouch: true,
  viewport: {width: 375, height: 667}, reducedMotion: 'reduce',
  extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
let outside = 0, syntheticCreatedRecords = 0;
const checks = {}, geometry = [], errors = [];
let failure;
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++; return route.abort();
});
await context.addInitScript(() => {
  localStorage.setItem('priceyard_onboarding_seen', '1');
  localStorage.setItem('priceyard_data_saver', '1');
  localStorage.setItem('priceyard_easy_reading', '1');
});
const page = await context.newPage();
page.setDefaultTimeout(10000); page.setDefaultNavigationTimeout(12000);
page.on('pageerror', error => errors.push(error.message));
const graphGeometry = () => page.evaluate(() => {
  const result = document.querySelector('#history-chart-results');
  const svg = result?.querySelector('svg');
  const headerBottom = document.querySelector('.site-header').getBoundingClientRect().bottom;
  const box = result.getBoundingClientRect(), plot = svg?.getBoundingClientRect();
  return {focused: document.activeElement === result, headerBottom, resultTop: box.top,
    svgTop: plot?.top, svgBottom: plot?.bottom,
    visiblePlot: plot ? Math.max(0, Math.min(innerHeight, plot.bottom) - Math.max(headerBottom, plot.top)) : 0,
    overflow: document.documentElement.scrollWidth > innerWidth + 1};
});
const assertGraphRevealed = async () => {
  await page.waitForFunction(() => document.activeElement?.id === 'history-chart-results');
  const state = await graphGeometry();
  assert.equal(state.focused, true); assert.equal(state.overflow, false);
  assert.ok(state.resultTop >= state.headerBottom + 9 && state.resultTop <= state.headerBottom + 16,
    `Results must clear sticky header: ${JSON.stringify(state)}`);
  assert.ok(state.visiblePlot >= 100, `Actual graph must be visible, not merely below fold: ${JSON.stringify(state)}`);
  geometry.push({control: 'mobile graph', ...state});
};

try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(response => response.json()));
  assert.equal(status.synthetic_only, true);
  const original = await page.evaluate(() => fetch('/api/price-updates').then(response => response.json()));
  const base = original[0]; assert.ok(base?.commodity_id && base?.market_id);
  const record = (index, overrides = {}) => ({...base, id: 19300 + index,
    unit: '1 container', bag_size: 'Recorded size', commodity_type: 'Recorded type',
    price_low: 40000 + index * 1000, price_high: 43000 + index * 1000, average_price: null,
    update_date_time: `2026-06-${String(index + 1).padStart(2, '0')}T10:00:00Z`, ...overrides});
  let history = [record(0), record(1), record(2),
    record(3, {bag_size: null, commodity_type: null}), record(4, {bag_size: null, commodity_type: null})];
  let historyFailure = false;
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route =>
    historyFailure ? route.fulfill({status: 503, json: {detail: 'Synthetic history unavailable'}})
      : route.fulfill({json: history}));

  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('admin@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  const historyPath = `/history?commodity_id=${base.commodity_id}&market_id=${base.market_id}`;
  await page.goto(origin + historyPath);
  await page.locator('.history-table-view tbody tr').nth(4).waitFor({state: 'attached'});
  assert.ok(await page.evaluate(() => scrollY < 5), 'Initial history loading must leave the title/filters in place');
  const shortcut = page.getByRole('button', {name: 'View price graph', exact: true});
  await shortcut.click(); await assertGraphRevealed();
  checks.mobile_easy_reading_graph_shortcut_reveals_actual_plot_below_sticky_header = true;

  const form = page.locator('.history-filters');
  await form.getByRole('button', {name: 'Search history', exact: true}).click();
  await page.waitForFunction(() => !document.querySelector('.history-filters button')?.disabled);
  await assertGraphRevealed();
  checks.successful_explicit_search_focuses_and_reveals_graph_without_initial_load_jump = true;
  const complete = page.locator('.trend-chart').filter({hasText: 'Recorded size'});
  const legacy = page.locator('.trend-chart').filter({hasText: 'Size not recorded'});
  assert.equal(await complete.locator('.trend-line').count(), 1);
  assert.equal(await complete.locator('.trend-area').count(), 1);
  assert.equal(await complete.locator('.trend-band').count(), 1);
  assert.equal(await legacy.locator('.trend-line, .trend-area, .trend-band').count(), 0);
  assert.equal(await legacy.locator('.trend-dot').count(), 2);
  assert.equal(await page.locator('.history-table-view tbody tr').count(), 5);
  assert.ok(await complete.locator('.trend-line').evaluate(node => parseFloat(getComputedStyle(node).strokeWidth) >= 3));
  await complete.locator('.trend-plot').focus(); await page.keyboard.press('Home');
  assert.match(await complete.locator('.trend-selection').innerText(), /40,000/);
  await page.keyboard.press('End');
  assert.match(await complete.locator('.trend-selection').innerText(), /45,000/);
  checks.area_and_prominent_line_only_join_comparable_records_with_ranges_and_inspection_preserved = true;
  await page.screenshot({path: path.join(runtime, 'price-usability-graph-mobile.png'), fullPage: false});

  historyFailure = true;
  const search = form.getByRole('button', {name: 'Search history', exact: true});
  await search.scrollIntoViewIfNeeded();
  await page.evaluate(() => {
    window.__priceyardTestScrollCalls = [];
    const original = window.scrollTo.bind(window);
    window.scrollTo = (...args) => { window.__priceyardTestScrollCalls.push(args); original(...args); };
  });
  await search.click();
  await page.getByText('Synthetic history unavailable', {exact: true}).waitFor();
  assert.notEqual(await page.evaluate(() => document.activeElement?.id), 'history-chart-results');
  // Removing long results can naturally clamp scrollY as the document shortens.
  // The application must not explicitly scroll/focus the stale results.
  assert.deepEqual(await page.evaluate(() => window.__priceyardTestScrollCalls), [],
    'A failed request must not programmatically scroll users to stale results');
  checks.failed_search_keeps_filter_position_and_shows_error = true;
  historyFailure = false;
  history = [record(0)];
  await page.goto(origin + historyPath); await page.locator('.history-single-price').waitFor();
  assert.equal(await page.getByRole('button', {name: 'View price graph', exact: true}).count(), 0);
  await page.getByRole('button', {name: 'View recorded prices', exact: true}).click();
  assert.equal(await page.locator('#history-chart-results svg').count(), 0);
  assert.match(await page.locator('#history-chart-results').innerText(), /One price recorded; no trend available yet/);
  checks.singleton_keeps_honest_summary_and_does_not_promise_a_trend_graph = true;

  await page.goto(origin + '/prices');
  for (const width of [320, 375, 1366]) {
    await page.setViewportSize({width, height: 667});
    const pause = page.getByRole('button', {name: 'Pause scrolling', exact: true});
    await pause.waitFor();
    const state = await pause.evaluate(node => {
      const box = node.getBoundingClientRect();
      const viewport = document.querySelector('.price-ticker-viewport').getBoundingClientRect();
      return {top: box.top, bottom: box.bottom, width: box.width, height: box.height,
        left: box.left, right: box.right, trackTop: viewport.top, trackBottom: viewport.bottom,
        trackWidth: viewport.width, screenWidth: innerWidth,
        overflow: document.documentElement.scrollWidth > innerWidth + 1};
    });
    assert.equal(state.overflow, false); assert.ok(state.top >= state.trackBottom - 1);
    assert.ok(state.width >= 24 && state.width <= 110 && state.height >= 24 && state.height <= 36);
    assert.ok(state.left >= 0 && state.right <= width + 1);
    assert.ok(state.trackWidth >= width - 2, 'Ticker controls must not take horizontal track space');
    geometry.push({control: 'ticker', width, ...state});
  }
  await page.emulateMedia({reducedMotion: 'no-preference'});
  const ticker = page.locator('.price-ticker-track');
  await page.getByRole('button', {name: 'Pause scrolling', exact: true}).focus();
  await page.keyboard.press('Enter');
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'paused');
  await page.getByRole('button', {name: 'Resume scrolling', exact: true}).click();
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'running');
  const running = await ticker.evaluate(node => getComputedStyle(node).transform);
  await page.waitForTimeout(150);
  assert.notEqual(await ticker.evaluate(node => getComputedStyle(node).transform), running);
  await page.emulateMedia({reducedMotion: 'reduce'});
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationName), 'none');
  checks.compact_ticker_control_sits_below_full_width_animation_and_pause_resume_remain_operable = true;

  // Existing guarded backend is in-memory synthetic data; no external writes.
  // Prefill is stubbed to a past up claim, to prove it cannot contaminate a new claim.
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/admin/latest', route =>
    route.fulfill({json: {...base, id: 19399, movement: 'up', unit: '1 bag', bag_size: 'Unknown',
      commodity_type: null, confidence_level: 'Reporter submitted', source_1: null, source_2: null}}));
  await page.setViewportSize({width: 375, height: 667});
  await page.goto(origin + '/admin/prices');
  const create = page.locator('form.admin-form').first();
  await create.locator('[name=commodity_id]').selectOption({label: 'Egusi'});
  await create.locator('[name=market_id]').selectOption({label: 'Kwali Market'});
  const movement = create.locator('[name=movement]');
  assert.equal(await movement.inputValue(), 'unknown');
  await create.getByRole('button', {name: 'Prefill from last entry', exact: true}).click();
  await page.locator('.status-box.success').filter({hasText: 'Your Movement choice was kept'}).waitFor();
  assert.equal(await movement.inputValue(), 'unknown');
  await movement.selectOption('down');
  await create.getByRole('button', {name: 'Prefill from last entry', exact: true}).click();
  await page.waitForFunction(() => !document.querySelector('form.admin-form button')?.disabled);
  assert.equal(await movement.inputValue(), 'down');
  checks.prefill_keeps_unknown_default_and_preserves_an_explicit_movement_choice = true;

  await create.getByLabel('Low', {exact: true}).fill('100');
  await create.getByLabel('High', {exact: true}).fill('200');
  await create.getByLabel('Average', {exact: true}).fill('150');
  await create.getByLabel('Update date/time', {exact: true}).fill('2026-10-22T12:00');
  await movement.selectOption('up');
  const created = page.waitForResponse(response => response.url() === origin + '/api/price-updates'
    && response.request().method() === 'POST');
  await create.getByRole('button', {name: 'Create pending update', exact: true}).click();
  const createdResponse = await created;
  assert.equal(createdResponse.status(), 201);
  const saved = await createdResponse.json(); syntheticCreatedRecords++;
  assert.equal(saved.movement, 'up'); assert.equal(Number(saved.price_low), 100);
  await page.waitForFunction(id => document.querySelector('.admin-action-panel input')?.value === String(id), saved.id);
  assert.equal(await create.getByLabel('Low', {exact: true}).inputValue(), '100');
  assert.equal(await create.getByLabel('High', {exact: true}).inputValue(), '200');
  const approval = page.waitForResponse(response => response.url() === `${origin}/api/price-updates/${saved.id}/approve`
    && response.request().method() === 'PATCH');
  await page.locator('.admin-action-panel').getByRole('button', {name: 'Approve', exact: true}).click();
  const approved = await approval; assert.equal(approved.status(), 200);
  assert.equal((await approved.json()).movement, 'up');
  const correction = page.locator('form.admin-form').nth(1);
  await correction.locator('[name=movement]').selectOption('down');
  const corrected = page.waitForResponse(response => response.url() === `${origin}/api/price-updates/${saved.id}`
    && response.request().method() === 'PATCH');
  await correction.getByRole('button', {name: 'Save correction', exact: true}).click();
  const changed = await corrected; assert.equal(changed.status(), 200);
  const final = await changed.json(); assert.equal(final.movement, 'down'); assert.equal(final.status, 'approved');
  assert.equal(Number(final.price_low), 100);
  assert.equal(await page.getByRole('button', {name: 'Review movement', exact: true}).count(), 0);
  checks.original_manual_admin_create_approve_and_correct_preserve_selected_movement_and_prices = true;
  assert.equal(outside, 0); assert.deepEqual(errors, []);
} catch (error) {
  failure = error.stack || String(error);
  await page.screenshot({path: path.join(runtime, 'price-usability-corrections-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, failure, external_page_requests: outside,
    page_errors: errors, synthetic_only: true, production_connections: 0, synthetic_created_records: syntheticCreatedRecords};
  fs.writeFileSync(path.join(runtime, 'price-usability-corrections-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await browser.close();
  if (failure) process.exitCode = 1;
}
