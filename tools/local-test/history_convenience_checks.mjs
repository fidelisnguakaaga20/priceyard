// Serial, synthetic checks for history ordering, remembered filters and ticker controls.
// Run only against the guarded in-memory preview through run_browser.py.
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
const storageKey = 'priceyard_history_filters_v1';
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
await context.addInitScript(key => {
  localStorage.setItem('priceyard_onboarding_seen', '1');
  localStorage.setItem('priceyard_data_saver', '1');
  if (sessionStorage.getItem('test_block_history_storage') === '1') {
    const originalGet = Storage.prototype.getItem;
    const originalSet = Storage.prototype.setItem;
    Storage.prototype.getItem = function (name) {
      if (name === key) throw new DOMException('Synthetic storage denial', 'SecurityError');
      return originalGet.call(this, name);
    };
    Storage.prototype.setItem = function (name, value) {
      if (name === key) throw new DOMException('Synthetic storage denial', 'SecurityError');
      return originalSet.call(this, name, value);
    };
  }
}, storageKey);
const page = await context.newPage();
page.setDefaultTimeout(10000);
page.setDefaultNavigationTimeout(12000);
page.on('pageerror', error => errors.push(error.message));
const queries = [];
let priceRequests = 0;
page.on('request', request => {
  if (new URL(request.url()).pathname === '/api/price-updates' && request.method() === 'GET') priceRequests++;
});
const chosen = async (label, id) => {
  await page.waitForFunction(({label, id}) => {
    const element = [...document.querySelectorAll('.history-filters label')]
      .find(node => node.textContent.trim().startsWith(label))?.querySelector('select');
    return element?.value === (id == null ? '' : `id:${id}`);
  }, {label, id});
};
const writeRemembered = value => page.evaluate(({key, value}) => localStorage.setItem(key, value),
  {key: storageKey, value: typeof value === 'string' ? value : JSON.stringify(value)});
const waitHistory = async () => {
  await page.locator('.history-table-view tbody tr').nth(6).waitFor({state: 'attached'});
  await page.waitForFunction(() => !document.querySelector('.history-filters button')?.disabled);
};
const ranges = async selector => page.locator(selector).allTextContents();
const chartState = () => page.locator('.history-trends').evaluate(node => ({
  lines: [...node.querySelectorAll('.trend-line')].map(line => line.getAttribute('d')),
  dates: [...node.querySelectorAll('.trend-plot svg g title')].map(title => title.textContent),
  selected: [...node.querySelectorAll('.trend-selection time')].map(time => time.dateTime),
}));
try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(r => r.json()));
  assert.equal(status.synthetic_only, true);
  const original = await page.evaluate(() => fetch('/api/price-updates').then(r => r.json()));
  const base = original[0];
  assert.ok(base?.commodity?.id && base?.market?.id);
  const commodity = {...base.commodity, name: 'Synthetic first commodity'};
  const secondCommodity = {...base.commodity, id: 98103, name: 'Synthetic second commodity'};
  const fallbackCommodity = {...base.commodity, id: 98104, name: 'Egusi'};
  const market = {...base.market, name: 'Synthetic first market'};
  const secondMarket = {...base.market, id: 98102, name: 'Synthetic second market'};
  let generation = 0;
  let historyFailure = false;
  const makeRecord = (index, selectedCommodity = commodity, selectedMarket = market) => ({...base,
    id: 18100 + index, commodity: selectedCommodity, commodity_id: selectedCommodity.id,
    market: selectedMarket, market_id: selectedMarket.id,
    unit: '1 recorded container', bag_size: 'Recorded size', commodity_type: 'Recorded type',
    price_low: 40000 + index * 1000 + generation * 100,
    price_high: 43000 + index * 1000 + generation * 100,
    average_price: null, update_date_time: index === 6 ? 'date not confirmed'
      : index === 1 ? '2026-06-02T23:45:00Z'
      : index === 2 ? '2026-06-03T00:30:00+03:00'
      : new Date(Date.UTC(2026, 5, 1 + index, 10)).toISOString()});
  await page.route(url => url.origin === origin && url.pathname === '/api/commodities',
    route => route.fulfill({json: [commodity, secondCommodity, fallbackCommodity]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/markets',
    route => route.fulfill({json: [market, secondMarket]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates',
    route => route.fulfill({json: [makeRecord(0), makeRecord(1, secondCommodity, secondMarket)]}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history/pairs',
    route => route.fulfill({json: [commodity, secondCommodity, fallbackCommodity]
      .flatMap(item => [market, secondMarket].map(place => ({commodity: item, market: place})))}));
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => {
    const params = new URL(route.request().url()).searchParams;
    queries.push({query: params.toString(), generation});
    if (historyFailure) return route.fulfill({status: 503, json: {detail: 'Temporary synthetic failure'}});
    const selectedCommodity = [commodity, secondCommodity, fallbackCommodity]
      .find(item => String(item.id) === params.get('commodity_id')) || fallbackCommodity;
    const selectedMarket = [market, secondMarket]
      .find(item => String(item.id) === params.get('market_id')) || market;
    return route.fulfill({json: [3, 0, 4, 1, 5, 2, 6].map(index => makeRecord(index, selectedCommodity, selectedMarket))});
  });

  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('trial@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  const historyPath = `/history?commodity_id=${commodity.id}&market_id=${market.id}`;
  await page.goto(origin + historyPath);
  await waitHistory();
  const order = page.getByLabel('History order', {exact: true});
  assert.equal(await order.inputValue(), 'oldest');
  const oldest = await ranges('.history-table-view tbody tr td:nth-child(4)');
  const oldestCards = await ranges('.history-card-list .price-range');
  assert.equal(oldest.length, 7);
  assert.match(oldest[0], /40,000/);
  assert.match(oldest[1], /42,000/); // UTC time, rather than lexical timestamp order.
  assert.match(oldest[2], /41,000/);
  assert.match(oldest.at(-2), /45,000/);
  assert.match(oldest.at(-1), /46,000/); // Unconfirmed time stays visible at the end.
  const chartBefore = await chartState();
  assert.equal(chartBefore.lines.length, 1);
  assert.ok(chartBefore.dates[0].includes('1 Jun'));
  assert.ok(chartBefore.dates.at(-1).includes('6 Jun'));
  const beforeSortRequests = queries.length;
  await order.selectOption('newest');
  assert.deepEqual(await ranges('.history-table-view tbody tr td:nth-child(4)'),
    [...oldest.slice(0, -1).reverse(), oldest.at(-1)]);
  assert.deepEqual(await ranges('.history-card-list .price-range'),
    [...oldestCards.slice(0, -1).reverse(), oldestCards.at(-1)]);
  assert.deepEqual(await chartState(), chartBefore);
  assert.equal(queries.length, beforeSortRequests);
  await order.focus(); await page.keyboard.press('Home'); await page.keyboard.press('Enter');
  assert.equal(await order.inputValue(), 'oldest');
  await order.focus(); await page.keyboard.press('End'); await page.keyboard.press('Enter');
  assert.equal(await order.inputValue(), 'newest');
  await page.screenshot({path: path.join(runtime, 'history-convenience-desktop.png'), fullPage: false});
  checks.history_order_reverses_table_and_cards_only_without_chart_or_request_changes = true;

  await page.locator('.history-filters select').nth(0).selectOption(`id:${secondCommodity.id}`);
  await page.locator('.history-filters select').nth(1).selectOption(`id:${secondMarket.id}`);
  await page.locator('.history-filters select').nth(2).selectOption('closing');
  await page.getByRole('button', {name: 'Search history', exact: true}).click();
  await waitHistory();
  assert.deepEqual(await page.evaluate(key => JSON.parse(localStorage.getItem(key)), storageKey),
    {commodity_id: secondCommodity.id, market_id: secondMarket.id});
  historyFailure = true;
  await page.locator('.history-filters select').nth(0).selectOption(`id:${commodity.id}`);
  await page.locator('.history-filters select').nth(1).selectOption(`id:${market.id}`);
  await page.getByRole('button', {name: 'Search history', exact: true}).click();
  await page.locator('.status-box.error').waitFor();
  assert.deepEqual(await page.evaluate(key => JSON.parse(localStorage.getItem(key)), storageKey),
    {commodity_id: secondCommodity.id, market_id: secondMarket.id});
  historyFailure = false;
  checks.failed_history_search_preserves_the_last_successful_saved_filters = true;
  secondCommodity.name = 'Renamed synthetic commodity'; secondMarket.name = 'Renamed synthetic market';
  generation++;
  const beforeReload = queries.length;
  await page.goto(origin + '/history'); await waitHistory();
  await chosen('Commodity', secondCommodity.id); await chosen('Market', secondMarket.id);
  assert.equal(await page.locator('.history-filters select').nth(0).locator('option:checked').textContent(), secondCommodity.name);
  assert.equal(await page.locator('.history-filters select').nth(1).locator('option:checked').textContent(), secondMarket.name);
  assert.equal(await page.locator('.history-filters select').nth(2).inputValue(), '');
  assert.ok(queries.length > beforeReload);
  assert.equal(queries.at(-1).generation, 1);
  assert.match((await ranges('.history-table-view tbody tr td:nth-child(4)'))[0], /40,100/);
  checks.submitted_filters_survive_reload_by_ids_with_fresh_prices_and_renamed_labels = true;

  await writeRemembered({commodity_id: secondCommodity.id, market_id: secondMarket.id});
  await page.goto(origin + historyPath); await waitHistory();
  await chosen('Commodity', commodity.id); await chosen('Market', market.id);
  await writeRemembered({commodity_id: secondCommodity.id, market_id: secondMarket.id});
  await page.goto(origin + `/history?commodity_id=${commodity.id}`); await waitHistory();
  await chosen('Commodity', commodity.id); await chosen('Market', null);
  assert.equal(new URLSearchParams(queries.at(-1).query).has('market_id'), false);
  checks.explicit_history_links_override_the_entire_remembered_pair = true;

  await writeRemembered({commodity_id: 999998, market_id: secondMarket.id});
  await page.goto(origin + '/history'); await waitHistory();
  await chosen('Commodity', fallbackCommodity.id); await chosen('Market', null);
  let query = new URLSearchParams(queries.at(-1).query);
  assert.equal(query.get('commodity_id'), String(fallbackCommodity.id));
  assert.equal(query.has('market_id'), false);
  await writeRemembered({commodity_id: secondCommodity.id, market_id: 999999});
  await page.goto(origin + '/history'); await waitHistory();
  await chosen('Commodity', secondCommodity.id); await chosen('Market', null);
  query = new URLSearchParams(queries.at(-1).query);
  assert.equal(query.get('commodity_id'), String(secondCommodity.id));
  assert.equal(query.has('market_id'), false);
  checks.removed_saved_records_do_not_send_stale_filter_ids = true;

  for (const value of ['{invalid json', JSON.stringify({commodity_id: -1, market_id: 'not an ID'})]) {
    await writeRemembered(value);
    await page.goto(origin + '/history'); await waitHistory();
    await chosen('Commodity', fallbackCommodity.id);
  }
  checks.malformed_preferences_safely_keep_the_original_default = true;
  await writeRemembered({commodity_id: null, market_id: null});
  await page.goto(origin + '/history'); await waitHistory();
  await chosen('Commodity', null); await chosen('Market', null);
  query = new URLSearchParams(queries.at(-1).query);
  assert.equal(query.has('commodity_id'), false); assert.equal(query.has('market_id'), false);
  checks.saved_empty_choices_preserve_the_users_all_records_search = true;

  await page.evaluate(() => sessionStorage.setItem('test_block_history_storage', '1'));
  await page.reload(); await waitHistory();
  await page.locator('.history-filters select').nth(0).selectOption(`id:${commodity.id}`);
  await page.locator('.history-filters select').nth(1).selectOption(`id:${market.id}`);
  await page.getByRole('button', {name: 'Search history', exact: true}).click();
  await waitHistory(); await chosen('Commodity', commodity.id); await chosen('Market', market.id);
  assert.equal(new URLSearchParams(queries.at(-1).query).get('commodity_id'), String(commodity.id));
  await page.evaluate(() => sessionStorage.removeItem('test_block_history_storage'));
  checks.blocked_browser_storage_does_not_break_history_or_search = true;

  await page.goto(origin + '/prices');
  const pause = page.getByRole('button', {name: 'Pause scrolling', exact: true});
  await pause.waitFor();
  const ticker = page.locator('.price-ticker-track');
  const tickerItems = await ticker.innerText();
  await page.emulateMedia({reducedMotion: 'no-preference'});
  const requestsBeforePause = priceRequests;
  await pause.focus(); await page.keyboard.press('Enter');
  const resume = page.getByRole('button', {name: 'Resume scrolling', exact: true});
  assert.equal(await resume.getAttribute('aria-pressed'), 'true');
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'paused');
  await page.mouse.move(1200, 850); await resume.evaluate(node => node.blur());
  const stoppedTransform = await ticker.evaluate(node => getComputedStyle(node).transform);
  await page.waitForTimeout(180);
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).transform), stoppedTransform);
  await resume.click();
  const pauseAgain = page.getByRole('button', {name: 'Pause scrolling', exact: true});
  // Resume must work while its button is still focused and under the pointer.
  assert.equal(await pauseAgain.evaluate(node => node === document.activeElement), true);
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'running');
  const resumedTransform = await ticker.evaluate(node => getComputedStyle(node).transform);
  await page.waitForTimeout(180);
  assert.notEqual(await ticker.evaluate(node => getComputedStyle(node).transform), resumedTransform);
  assert.equal(await ticker.innerText(), tickerItems);
  assert.equal(priceRequests, requestsBeforePause);
  checks.keyboard_ticker_pause_resume_stops_animation_without_altering_records_or_fetching = true;
  await page.emulateMedia({reducedMotion: 'reduce'});
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationName), 'none');
  await pauseAgain.click(); await page.getByRole('button', {name: 'Resume scrolling', exact: true}).click();
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationName), 'none');
  checks.ticker_respects_reduced_motion_even_after_resume = true;

  for (const width of [320, 375]) {
    await page.setViewportSize({width, height: 900});
    for (const easy of [false, true]) {
      const easyToggle = page.getByRole('button', {name: /^Easy reading:/});
      if (/On/.test(await easyToggle.innerText()) !== easy) await easyToggle.click();
      for (const dark of [false, true]) {
        const darkToggle = page.getByRole('button', {name: /^Dark mode:/});
        if (/On/.test(await darkToggle.innerText()) !== dark) await darkToggle.click();
        const state = await pauseAgain.evaluate(node => {
          const box = node.getBoundingClientRect();
          return {overflow: document.documentElement.scrollWidth > innerWidth + 1,
            width: box.width, height: box.height, left: box.left, right: box.right, viewport: innerWidth};
        });
        assert.equal(state.overflow, false); assert.ok(state.width >= 44 && state.height >= 44);
        assert.ok(state.left >= 0 && state.right <= width + 1);
        geometry.push({width, easy, dark, control: 'ticker', ...state});
      }
    }
    await page.goto(origin + historyPath); await waitHistory();
    await page.getByLabel('History order', {exact: true}).selectOption('newest');
    assert.equal(await page.locator('.history-card-list').isVisible(), true);
    assert.match((await ranges('.history-card-list .price-range'))[0], /45,100/);
    const state = await page.getByLabel('History order', {exact: true}).evaluate(node => {
      const box = node.getBoundingClientRect();
      return {overflow: document.documentElement.scrollWidth > innerWidth + 1,
        width: box.width, height: box.height, left: box.left, right: box.right};
    });
    assert.equal(state.overflow, false); assert.ok(state.height >= 44);
    assert.ok(state.left >= 0 && state.right <= width + 1);
    geometry.push({width, control: 'history order', ...state});
    if (width === 375) await page.screenshot({path: path.join(runtime, 'history-convenience-mobile.png'), fullPage: false});
    await page.goto(origin + '/prices'); await pauseAgain.waitFor();
  }
  checks.mobile_320_375_controls_and_newest_history_cards_fit_easy_reading_and_themes = true;
  assert.deepEqual(errors, []); assert.equal(outside, 0);
} catch (error) {
  failure = error.stack || String(error);
  await page.screenshot({path: path.join(runtime, 'history-convenience-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, failure,
    external_page_requests: outside, page_errors: errors, synthetic_only: true,
    production_connections: 0, database_changes: 0};
  fs.writeFileSync(path.join(runtime, 'history-convenience-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await browser.close();
  if (failure) process.exitCode = 1;
}
