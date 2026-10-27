// Bounded, serial synthetic checks. Run through run_browser.py against the guarded preview only.
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
  viewport: {width: 1366, height: 900}, reducedMotion: 'reduce',
  extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
const checks = {};
const geometry = [];
const errors = [];
let outside = 0;
let failure;
let historyRequests = 0;
let historyRows = [];
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
const periodGroup = () => page.getByRole('group', {name: 'History period', exact: true});
const periodButton = name => periodGroup().getByRole('button', {name, exact: true});
const rowIds = () => page.locator('.history-table-view tbody tr').evaluateAll(rows => rows.map(row =>
  Number(row.textContent.match(/Synthetic record (\d+)/)?.[1])));
const cardIds = () => page.locator('.history-card-list > article').evaluateAll(cards => cards.map(card =>
  Number(card.textContent.match(/Synthetic record (\d+)/)?.[1])));
const expectRows = async expected => {
  await page.waitForFunction(count => document.querySelectorAll('.history-table-view tbody tr').length === count,
    expected.length);
  assert.deepEqual([...(await rowIds())].sort((a, b) => a - b), [...expected].sort((a, b) => a - b));
  assert.deepEqual(await cardIds(), await rowIds());
};
const chartState = () => page.locator('.history-trends').evaluate(node => ({
  lines: [...node.querySelectorAll('.trend-line')].map(line => line.getAttribute('d')),
  points: node.querySelectorAll('.trend-dot').length,
  singles: node.querySelectorAll('.history-single-price').length,
  series: [...node.querySelectorAll('.trend-record-count')].map(element => element.textContent),
}));
const setPreference = async (prefix, enabled) => {
  const toggle = page.getByRole('button', {name: new RegExp(`^${prefix}:`)});
  if (/On/.test(await toggle.innerText()) !== enabled) await toggle.click();
};
try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(response => response.json()));
  assert.equal(status.synthetic_only, true);
  const original = await page.evaluate(() => fetch('/api/price-updates').then(response => response.json()));
  const base = original[0];
  assert.ok(base?.commodity?.id && base?.market?.id);
  const commodity = {...base.commodity, name: 'Synthetic palm oil'};
  const market = {...base.market, name: 'Synthetic market'};
  const day = 86400000;
  const offset = 3600000;
  const today = Math.floor((Date.now() + offset) / day) * day - offset;
  const sevenStart = today - 6 * day;
  const thirtyStart = today - 29 * day;
  const tomorrow = today + day;
  const dates = [sevenStart - 1, sevenStart, tomorrow - 1, tomorrow, thirtyStart, thirtyStart - 1,
    'date not confirmed', new Date(today).toISOString().slice(0, 19), today + 3600000, today + 7200000];
  const fixture = dates.map((date, index) => ({...base,
    id: 19100 + index, commodity, commodity_id: commodity.id, market, market_id: market.id,
    unit: '1 recorded container', bag_size: index === 8 ? 'Different recorded size' : 'Recorded size',
    commodity_type: 'Recorded type',
    price_low: index === 9 ? -1 : 40000 + index * 1000,
    price_high: 43000 + index * 1000, average_price: null,
    update_date_time: typeof date === 'number' ? new Date(date).toISOString() : date,
    possible_meaning: `Synthetic record ${index}`,
  }));
  historyRows = [fixture[6], fixture[3], fixture[5], fixture[8], fixture[1], fixture[7], fixture[2],
    fixture[9], fixture[0], fixture[4]];
  const fixtureBefore = JSON.stringify(historyRows);
  const currentRows = [fixture[1], fixture[8]];
  await page.route(url => url.origin === origin && url.pathname === '/api/commodities',
    route => route.fulfill({json: [commodity]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/markets',
    route => route.fulfill({json: [market]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates',
    route => route.fulfill({json: currentRows}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history/pairs',
    route => route.fulfill({json: [{commodity, market}]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => {
    historyRequests++; return route.fulfill({json: historyRows});
  });
  for (const endpoint of ['market-signals', 'quality-signals', 'buying-zones', 'sell-watch-windows',
    'storage-suitability', 'cost-breakdowns']) {
    await page.route(url => url.origin === origin && url.pathname === `/api/${endpoint}`,
      route => route.fulfill({json: []}));
  }
  const historyPath = `/history?commodity_id=${commodity.id}&market_id=${market.id}`;
  await page.goto(origin + historyPath);
  await page.getByRole('heading', {name: 'Price history', exact: true}).waitFor();
  await page.locator('.locked-panel').waitFor();
  assert.equal(await periodGroup().count(), 0);
  assert.equal(historyRequests, 0);
  checks.guest_history_gate_remains_and_does_not_request_private_history = true;

  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('trial@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  await page.goto(origin + historyPath);
  await expectRows([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
  assert.equal(await periodButton('All history').getAttribute('aria-pressed'), 'true');
  assert.equal(await periodButton('7 days').getAttribute('aria-pressed'), 'false');
  assert.equal(await periodButton('30 days').getAttribute('aria-pressed'), 'false');
  assert.match(await page.locator('.history-trends').innerText(), /unconfirmed date\/time/);
  const allChart = await chartState();
  assert.equal(allChart.points, 6);
  assert.equal(allChart.singles, 1);
  checks.all_history_default_preserves_ambiguous_dates_and_invalid_prices_in_both_lists = true;

  const requestsBeforePeriods = historyRequests;
  await periodButton('7 days').click();
  await expectRows([1, 2, 8, 9]);
  assert.equal(await periodButton('7 days').getAttribute('aria-pressed'), 'true');
  const sevenChart = await chartState();
  assert.equal(sevenChart.points, 2);
  assert.equal(sevenChart.singles, 1);
  assert.equal(sevenChart.lines.length, 1);
  const differentSizeSeries = page.locator('.history-price-series').filter({hasText: 'Different recorded size'});
  assert.equal(await differentSizeSeries.count(), 1);
  assert.equal(await differentSizeSeries.locator('.trend-line').count(), 0);
  assert.equal(await differentSizeSeries.locator('.trend-record-count').innerText(), '1 record');
  checks.seven_wat_calendar_days_include_start_and_today_but_exclude_previous_millisecond_and_tomorrow = true;

  await periodButton('30 days').click();
  await expectRows([0, 1, 2, 4, 8, 9]);
  assert.equal(await periodButton('30 days').getAttribute('aria-pressed'), 'true');
  const thirtyChart = await chartState();
  assert.equal(thirtyChart.points, 4);
  assert.equal(thirtyChart.singles, 1);
  assert.equal(await page.locator('.history-period-note').innerText(),
    'Records without a confirmed date are available in All history.');
  assert.equal(historyRequests, requestsBeforePeriods);
  checks.thirty_day_boundary_and_unconfirmed_date_notice_filter_every_view_without_refetching = true;

  const chronological = await rowIds();
  await page.getByLabel('History order', {exact: true}).selectOption('newest');
  assert.deepEqual(await rowIds(), [...chronological].reverse());
  assert.deepEqual(await cardIds(), [...chronological].reverse());
  assert.deepEqual(await chartState(), thirtyChart);
  await periodButton('All history').focus();
  await page.keyboard.press('Enter');
  await expectRows([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
  assert.equal(await periodButton('All history').getAttribute('aria-pressed'), 'true');
  assert.deepEqual(await chartState(), allChart);
  assert.equal(historyRequests, requestsBeforePeriods);
  assert.equal(JSON.stringify(historyRows), fixtureBefore);
  checks.history_order_only_changes_lists_and_all_history_restores_original_records = true;

  historyRows = [fixture[4], fixture[5]];
  await page.getByRole('button', {name: 'Search history', exact: true}).click();
  await expectRows([4, 5]);
  const beforeEmptyToggle = historyRequests;
  await periodButton('7 days').click();
  await expectRows([]);
  assert.equal(await page.locator('.history-trends').count(), 0);
  const empty = page.locator('#history-chart-results .status-box');
  await empty.waitFor();
  assert.match(await empty.innerText(), /All history/i);
  await periodButton('All history').click();
  await expectRows([4, 5]);
  assert.equal(historyRequests, beforeEmptyToggle);
  checks.empty_period_offers_all_history_recovery_without_losing_records_or_fetching = true;

  historyRows = [...fixture];
  await page.goto(origin + historyPath); await expectRows([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]);
  await page.setViewportSize({width: 375, height: 667});
  await periodButton('7 days').click(); await expectRows([1, 2, 8, 9]);
  assert.equal(await page.locator('.history-card-list').isVisible(), true);
  const mobilePeriods = await periodGroup().evaluate(node => {
    const bounds = node.getBoundingClientRect();
    return {left: bounds.left, right: bounds.right,
      overflow: document.documentElement.scrollWidth > innerWidth + 1,
      buttons: [...node.querySelectorAll('button')].map(button => {
        const rect = button.getBoundingClientRect();
        return {width: rect.width, height: rect.height};
      })};
  });
  assert.equal(mobilePeriods.overflow, false);
  assert.ok(mobilePeriods.left >= 0 && mobilePeriods.right <= 376);
  assert.ok(mobilePeriods.buttons.every(button => button.height >= 44));
  geometry.push({control: 'period', width: 375, ...mobilePeriods});
  await page.screenshot({path: path.join(runtime, 'period-polish-history-mobile.png'), fullPage: false});
  checks.mobile_period_controls_fit_and_mobile_prices_match_chart_period = true;

  await page.goto(origin + '/prices');
  const track = page.locator('.price-ticker-track');
  const pause = page.getByRole('button', {name: 'Pause scrolling', exact: true});
  await pause.waitFor();
  await page.mouse.move(0, 650);
  assert.equal((await pause.innerText()).trim(), 'Pause');
  assert.equal(await pause.evaluate(node => getComputedStyle(node).backgroundColor), 'rgb(246, 197, 107)');
  assert.equal(await pause.evaluate(node => getComputedStyle(node).color), 'rgb(37, 39, 24)');
  const trackBefore = await track.innerText();
  await pause.focus(); await page.keyboard.press('Enter');
  const resume = page.getByRole('button', {name: 'Resume scrolling', exact: true});
  assert.equal((await resume.innerText()).trim(), 'Resume');
  assert.equal(await resume.getAttribute('aria-pressed'), 'true');
  assert.equal(await resume.evaluate(node => getComputedStyle(node).backgroundColor), 'rgb(216, 236, 217)');
  assert.equal(await resume.evaluate(node => getComputedStyle(node).color), 'rgb(37, 39, 24)');
  assert.equal(await resume.evaluate(node => getComputedStyle(node).outlineStyle), 'solid');
  assert.equal(await track.evaluate(node => getComputedStyle(node).animationName), 'none');
  await page.keyboard.press('Space');
  assert.equal(await pause.getAttribute('aria-pressed'), 'false');
  assert.equal(await track.innerText(), trackBefore);
  checks.word_only_ticker_colors_keyboard_focus_pause_resume_and_reduced_motion_pass = true;

  for (const width of [320, 375, 1366]) {
    await page.setViewportSize({width, height: width < 640 ? 667 : 900});
    for (const easy of [false, true]) {
      await setPreference('Easy reading', easy);
      for (const dark of [false, true]) {
        await setPreference('Dark mode', dark);
        await page.mouse.move(0, width < 640 ? 650 : 850);
        const state = await pause.evaluate(node => {
          const box = node.getBoundingClientRect();
          const viewport = document.querySelector('.price-ticker-viewport').getBoundingClientRect();
          const ticker = node.closest('.price-ticker-controls').getBoundingClientRect();
          return {left: box.left, right: box.right, width: box.width, height: box.height,
            top: box.top, trackBottom: viewport.bottom, trackWidth: viewport.width, tickerWidth: ticker.width,
            color: getComputedStyle(node).backgroundColor,
            overflow: document.documentElement.scrollWidth > innerWidth + 1};
        });
        assert.equal(state.overflow, false);
        assert.ok(state.left >= 0 && state.right <= width + 1);
        assert.ok(state.width >= 64 && state.height >= 24);
        assert.ok(state.top >= state.trackBottom - 1);
        assert.ok(Math.abs(state.trackWidth - state.tickerWidth) <= 2);
        assert.equal(state.color, 'rgb(246, 197, 107)');
        geometry.push({control: 'ticker', viewportWidth: width, easy, dark, ...state});
      }
    }
  }
  checks.compact_ticker_stays_below_full_width_animation_in_easy_reading_and_both_themes = true;

  const detailPath = `/commodities/${encodeURIComponent(commodity.name)}?commodity_id=${commodity.id}`;
  await page.route(url => url.origin === origin && url.pathname === `/api/commodities/${commodity.id}`,
    route => route.fulfill({json: commodity}));
  await page.goto(origin + detailPath);
  await page.locator('.commodity-detail-page .intelligence-grid > .card').nth(5).waitFor();
  assert.equal((await page.locator('.commodity-intro-copy .eyebrow').textContent()).trim(), 'Full-access intelligence');
  assert.equal(await page.locator('.commodity-detail-page .detail-card').count(), 0);
  for (const width of [375, 1366]) {
    await page.setViewportSize({width, height: width === 375 ? 667 : 900});
    for (const easy of [false, true]) {
      await setPreference('Easy reading', easy);
      await page.evaluate(() => scrollTo(0, 0));
      const state = await page.locator('.commodity-detail-page').evaluate(node => {
        const header = document.querySelector('.site-header').getBoundingClientRect();
        const intro = node.querySelector('.commodity-page-intro').getBoundingClientRect();
        const image = node.querySelector('.commodity-image-detail').getBoundingClientRect();
        const copy = node.querySelector('.commodity-intro-copy').getBoundingClientRect();
        const card = node.querySelector('.intelligence-grid > .card').getBoundingClientRect();
        return {headerBottom: header.bottom, introHeight: intro.height, imageWidth: image.width,
          imageRight: image.right, copyLeft: copy.left, cardTop: card.top,
          overflow: document.documentElement.scrollWidth > innerWidth + 1};
      });
      assert.equal(state.overflow, false);
      assert.equal(Math.round(state.imageWidth), width === 375 ? 56 : 80);
      assert.ok(state.imageRight <= state.copyLeft);
      assert.ok(state.cardTop - state.headerBottom <= (easy ? 420 : 380));
      assert.ok(state.cardTop < (width === 375 ? 667 : 900));
      geometry.push({control: 'commodity intro', viewportWidth: width, easy, ...state});
    }
    await page.screenshot({path: path.join(runtime, `period-polish-commodity-${width}.png`), fullPage: false});
  }
  checks.compact_commodity_intro_brings_intelligence_first_without_repeated_price_cards = true;
  assert.deepEqual(errors, []);
  assert.equal(outside, 0);
} catch (error) {
  failure = error.stack || String(error);
  await page.screenshot({path: path.join(runtime, 'period-polish-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, failure,
    history_requests: historyRequests, external_page_requests: outside, page_errors: errors,
    synthetic_only: true, production_connections: 0, database_changes: 0};
  fs.writeFileSync(path.join(runtime, 'period-and-polish-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await browser.close();
  if (failure) process.exitCode = 1;
}
