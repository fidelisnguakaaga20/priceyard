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
const context = await browser.newContext({serviceWorkers: 'block', hasTouch: true, viewport: {width: 1366, height: 900}, extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
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
  assert.equal(await page.locator('.price-option').count(), 2);
  assert.equal(await page.locator('.price-option-select').count(), 1);
  const rawOptions = await page.locator('.price-option-select option').evaluateAll(options => options.map(option => Number(option.value)));
  assert.deepEqual(rawOptions.sort((a, b) => a - b), [101, 102]);
  for (const option of await page.locator('.price-option').all()) {
    assert.equal(await option.getByRole('link', {name: 'Share on WhatsApp', exact: true}).count(), 1);
    assert.equal(await option.getByRole('link', {name: 'Market insights', exact: true}).count(), 1);
    assert.equal(await option.getByRole('link', {name: /Log in to watch/}).count(), 1);
  }
  assert.match(await page.locator('.price-option').nth(0).innerText(), /Recorded size two/);
  await page.locator('.price-option-select').selectOption('101');
  assert.match(await page.locator('.price-option').nth(0).innerText(), /Recorded size one/);
  await page.locator('.price-option-select').selectOption('102');
  assert.match(await page.locator('.price-option').nth(0).innerText(), /Recorded size two/);
  assert.match(await page.locator('.price-option').nth(1).innerText(), /Synthetic second market/);
  checks.one_photo_compact_markets_all_variants_and_guest_actions = true;
  // Same commodity name with a different ID must never be collapsed.
  shownCurrent = [...current, price(104, {commodity_id: 9003, commodity: {...base.commodity, id: 9003}})];
  await page.reload(); await page.locator('.price-option').nth(2).waitFor();
  assert.equal(await page.locator('.commodity-price-card').count(), 2);
  checks.commodity_ids_not_names_control_grouping = true;
  await page.locator('.filter-bar select').nth(0).selectOption({label: base.commodity.name});
  shownCurrent = [current[1]];
  await page.getByRole('button', {name: 'Search prices', exact: true}).click();
  await page.waitForFunction(() => document.querySelectorAll('.price-option').length === 1);
  assert.match(await page.locator('.price-option').innerText(), /Recorded size two/);
  checks.filters_replace_grouped_results = true;
  shownCurrent = current;
  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('trial@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  await page.goto(origin + '/prices'); await page.locator('.price-option').nth(1).waitFor();
  let watchedBody;
  await page.route(origin + '/api/watchlist', async route => {
    watchedBody = route.request().postDataJSON();
    await route.fulfill({status: 201, json: {id: 1}});
  });
  await page.locator('.price-option').nth(1).getByRole('button', {name: /Get price alerts/}).click();
  await page.locator('.price-option').nth(1).getByRole('button', {name: /Alerts on/}).waitFor();
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
  // A lone saved price is a concise summary, never an oversized empty plot.
  // Zero prices are legitimate and must still be presented as recorded.
  history = [price(207, {price_low: 0, price_high: 0})];
  await page.reload(); await page.locator('.history-table-view tbody tr').waitFor();
  assert.equal(await page.locator('.history-single-price').count(), 1);
  assert.equal(await page.locator('.trend-chart').count(), 0);
  assert.equal(await page.locator('.trend-line').count(), 0);
  assert.equal(await page.locator('.history-price-series svg').count(), 0);
  const single = await page.locator('.history-single-price').innerText();
  assert.match(single, /₦0/);
  assert.match(single, /2026/);
  assert.match(single, /One price recorded; no trend available yet\./);
  checks.single_zero_price_uses_compact_dated_summary = true;
  history = [price(208, {update_date_time: '2026-06-01T12:00:00'}), price(209, {price_high: -1}),
    price(210, {average_price: 999999}), price(211)];
  await page.reload(); await page.locator('.history-table-view tbody tr').nth(3).waitFor();
  assert.equal(await page.locator('.trend-dot').count(), 0);
  assert.equal(await page.locator('.history-single-price').count(), 1);
  assert.equal(await page.locator('.history-table-view tbody tr').count(), 4);
  await page.getByText(/They remain in the history below/).waitFor();
  checks.invalid_prices_and_ambiguous_times_not_plotted_but_retained = true;
  // Selection follows recorded time, not API response order or equal spacing.
  // Different ranges make each selected record distinguishable to the reader.
  history = [
    price(223, {update_date_time: '2026-06-10T10:00:00Z', price_low: 50000, price_high: 53000}),
    price(221, {update_date_time: '2026-06-01T10:00:00Z'}),
    price(222, {update_date_time: '2026-06-03T10:00:00Z', price_low: 45000, price_high: 48000}),
  ];
  await page.reload(); await page.locator('.trend-chart').waitFor();
  const interactiveChart = page.locator('.trend-chart');
  const plot = interactiveChart.locator('.trend-plot');
  const selection = interactiveChart.locator('.trend-selection');
  assert.ok(await interactiveChart.locator('.trend-y-tick').count() >= 2);
  assert.ok(await interactiveChart.locator('.trend-x-tick').count() >= 2);
  assert.ok(await interactiveChart.locator('.trend-grid-line').count() >= 2);
  for (const tick of await interactiveChart.locator('.trend-y-tick').all()) assert.match(await tick.textContent(), /₦/);
  assert.match((await interactiveChart.locator('.trend-x-tick').allTextContents()).join(' '), /Jun/);
  await plot.focus(); await plot.press('Home');
  assert.match(await selection.innerText(), /1 Jun(?:e)? 2026/);
  assert.match(await selection.innerText(), /₦40,000/);
  assert.match(await selection.innerText(), /₦43,000/);
  assert.match(await selection.innerText(), /WAT/);
  await plot.press('ArrowRight');
  assert.match(await selection.innerText(), /3 Jun(?:e)? 2026/);
  assert.match(await selection.innerText(), /₦45,000/);
  await plot.press('End');
  assert.match(await selection.innerText(), /10 Jun(?:e)? 2026/);
  assert.match(await selection.innerText(), /₦53,000/);
  await interactiveChart.getByRole('button', {name: 'Previous recorded price', exact: true}).click();
  assert.match(await selection.innerText(), /3 Jun(?:e)? 2026/);
  await interactiveChart.getByRole('button', {name: 'Next recorded price', exact: true}).click();
  assert.match(await selection.innerText(), /10 Jun(?:e)? 2026/);
  checks.readable_axes_grid_and_keyboard_chronological_selection = true;
  const plotBounds = await plot.boundingBox(); assert.ok(plotBounds);
  await plot.click({position: {x: 2, y: plotBounds.height / 2}});
  assert.match(await selection.innerText(), /1 Jun(?:e)? 2026/);
  await plot.click({position: {x: plotBounds.width - 2, y: plotBounds.height / 2}});
  assert.match(await selection.innerText(), /10 Jun(?:e)? 2026/);
  checks.pointer_selection_shows_exact_record_details = true;
  await page.setViewportSize({width: 375, height: 812});
  await plot.scrollIntoViewIfNeeded();
  const touchBounds = await plot.boundingBox(); assert.ok(touchBounds);
  await page.touchscreen.tap(touchBounds.x + 2, touchBounds.y + touchBounds.height / 2);
  assert.match(await selection.innerText(), /1 Jun(?:e)? 2026/);
  await page.touchscreen.tap(touchBounds.x + touchBounds.width - 2, touchBounds.y + touchBounds.height / 2);
  assert.match(await selection.innerText(), /10 Jun(?:e)? 2026/);
  checks.mobile_tap_shows_exact_record_details = true;
  await page.setViewportSize({width: 1366, height: 900});
  // A matching flat series has finite coordinates and its dates remain distinct.
  history = [price(231, {price_low: 0, price_high: 0, update_date_time: '2026-06-01T10:00:00Z'}),
    price(232, {price_low: 0, price_high: 0, update_date_time: '2026-06-02T10:00:00Z'})];
  await page.reload(); await page.locator('.trend-chart').waitFor();
  assert.equal(await page.locator('.trend-line').count(), 1);
  const flatCoordinates = await page.locator('.trend-dot').evaluateAll(nodes => nodes.map(node =>
    ({x: Number(node.getAttribute('cx')), y: Number(node.getAttribute('cy'))})));
  assert.equal(flatCoordinates.length, 2);
  assert.ok(flatCoordinates.every(point => Number.isFinite(point.x) && Number.isFinite(point.y)));
  assert.ok(flatCoordinates[0].x < flatCoordinates[1].x);
  assert.equal(flatCoordinates[0].y, flatCoordinates[1].y);
  checks.flat_matching_series_remains_readable = true;
  // Same-time observations cannot establish movement over time. Keep both
  // recorded prices reachable rather than joining them into a vertical trend.
  history = [price(242, {price_low: 45000, price_high: 48000, update_date_time: '2026-06-01T10:00:00Z'}),
    price(241, {update_date_time: '2026-06-01T10:00:00Z'})];
  await page.reload(); await page.locator('.trend-chart').waitFor();
  assert.equal(await page.locator('.trend-line').count(), 0);
  assert.equal(await page.locator('.trend-dot').count(), 2);
  const tiedPlot = page.locator('.trend-plot');
  await tiedPlot.focus(); await tiedPlot.press('Home');
  assert.match(await page.locator('.trend-selection').innerText(), /₦40,000/);
  await tiedPlot.press('End');
  assert.match(await page.locator('.trend-selection').innerText(), /₦48,000/);
  const tiedXs = await page.locator('.trend-dot').evaluateAll(nodes => nodes.map(node => Number(node.getAttribute('cx'))));
  assert.equal(tiedXs[0], tiedXs[1]);
  checks.same_time_records_remain_separate_and_keyboard_accessible = true;
  history = [price(251, {update_date_time: '2026-06-01T10:00:00Z'}),
    price(252, {update_date_time: '2026-06-01T15:00:00Z'})];
  await page.reload(); await page.locator('.trend-chart').waitFor();
  assert.equal(await page.locator('.trend-line').count(), 1);
  assert.match(await page.locator('.trend-axis-captions').innerText(), /Time \(WAT\)/);
  const timeLabels = await page.locator('.trend-x-tick').allTextContents();
  assert.equal(new Set(timeLabels).size, timeLabels.length);
  assert.match(timeLabels[0], /11:00/);
  checks.same_day_prices_have_distinct_wat_time_ticks = true;
  history = [price(201), price(202), price(205, {bag_size: null, commodity_type: null})];
  const geometry = [];
  for (const width of [375, 1366]) for (const theme of ['dark', 'light']) {
    await page.setViewportSize({width, height: 900});
    await page.evaluate(theme => { localStorage.setItem('priceyard_dark_mode', theme === 'dark' ? '1' : '0');
      localStorage.setItem('priceyard_easy_reading', '1'); }, theme);
    await page.goto(origin + '/prices'); await page.locator('.price-option').nth(1).waitFor();
    assert.equal(await page.locator('.commodity-price-card .commodity-image').count(), 1);
    const cardsFit = await page.locator('.price-option').evaluateAll(nodes => nodes.every(node => node.scrollWidth <= node.clientWidth + 1));
    assert.equal(cardsFit, true, 'Grouped price contents must fit');
    await page.goto(origin + '/history'); await page.locator('.history-single-price').waitFor();
    assert.equal(await page.locator('.trend-chart').count(), 1);
    assert.equal(await page.locator('.history-single-price').count(), 1);
    await page.evaluate(theme => document.documentElement.dataset.theme = theme, theme);
    const state = await page.locator('.trend-line').evaluate(node => ({stroke: getComputedStyle(node).stroke,
      color: getComputedStyle(document.documentElement).getPropertyValue('--color-link').trim(),
      overflow: document.documentElement.scrollWidth > innerWidth}));
    assert.equal(state.overflow, false);
    assert.ok(state.stroke !== 'rgb(0, 0, 0)' && state.stroke !== 'none');
    const svgBounds = await page.locator('.trend-chart svg').boundingBox(); assert.ok(svgBounds);
    assert.ok(svgBounds.height <= 260, `Chart must remain compact at width ${width}`);
    assert.ok(svgBounds.height >= 140, `Chart must remain usable at width ${width}`);
    assert.ok(await page.locator('.trend-chart .trend-selection').isVisible());
    geometry.push({width, theme, stroke: state.stroke, plot_height: svgBounds.height});
    if (width === 375 && theme === 'dark') await page.screenshot({path: path.join(lab, 'runtime/price-history-restored-mobile.png'), fullPage: true});
  }
  checks.mobile_easy_reading_and_theme_compatible_graphs = true;
  // Review a realistic month-spanning history, including incomplete records
  // and an isolated old measurement. Fabricated values only; no API writes.
  const historical = Array.from({length: 18}, (_, index) => price(300 + index, {
    update_date_time: new Date(Date.UTC(2026, 4, 25) + index * 8 * 86400000).toISOString(),
    price_low: 40000 + index * 1000 + (index % 3) * 2000,
    price_high: 43000 + index * 1000 + (index % 3) * 2000,
    notes: null,
  }));
  history = [...historical, ...historical.slice(0, 8).map((item, index) => ({...item, id: 400 + index, bag_size: null, commodity_type: null})),
    price(450, {bag_size: 'Separate recorded size', price_low: 175000, price_high: 180000, notes: null})];
  await page.setViewportSize({width: 375, height: 900});
  await page.goto(origin + '/history'); await page.locator('.history-single-price').waitFor();
  assert.equal(await page.locator('.trend-chart').count(), 2);
  assert.equal(await page.locator('.trend-line').count(), 1);
  assert.equal(await page.locator('.trend-dot').count(), 26);
  await page.locator('.history-trends').screenshot({path: path.join(lab, 'runtime/price-history-restored-mobile.png')});
  await page.setViewportSize({width: 1366, height: 900});
  await page.goto(origin + '/prices'); await page.locator('.price-option').nth(1).waitFor();
  await page.screenshot({path: path.join(lab, 'runtime/grouped-commodity-prices.png'), fullPage: true});
  await page.goto(origin + '/history'); await page.locator('.history-single-price').waitFor();
  await page.locator('.history-trends').screenshot({path: path.join(lab, 'runtime/price-history-restored.png')});
  assert.equal(outside, 0); assert.deepEqual(errors, []);
  const report = {passed: Object.keys(checks).length, checks, geometry, external_page_requests: outside, production_connections: 0,
    synthetic_only: true, database_changes: 0};
  fs.writeFileSync(path.join(lab, 'runtime/price-presentation-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
} finally { await browser.close(); }
