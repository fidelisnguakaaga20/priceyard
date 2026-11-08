// Focused, synthetic-only Current Prices checks. Run via run_browser.py against
// the existing guarded preview; no production/provider requests or price writes.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
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
let outside = 0;
let currentRequests = 0;
let historyRequests = 0;
let failure;
const checks = {};
const geometry = [];
const errors = [];
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++; return route.abort();
});
await context.addInitScript(() => {
  localStorage.setItem('priceyard_onboarding_seen', '1');
  localStorage.setItem('priceyard_data_saver', '0');
  // Invoke the application's actual minute callback without sleeping a minute.
  // Other browser timers retain their real behavior. This changes test timing,
  // not request/selection logic, and is never included in application assets.
  const nativeInterval = window.setInterval.bind(window);
  const nativeClear = window.clearInterval.bind(window);
  const callbacks = new Map();
  let intervalId = -1;
  window.setInterval = (callback, delay, ...args) => {
    if (delay !== 60_000 || typeof callback !== 'function') return nativeInterval(callback, delay, ...args);
    const id = intervalId--;
    callbacks.set(id, () => callback(...args));
    return id;
  };
  window.clearInterval = id => { if (!callbacks.delete(id)) nativeClear(id); };
  window.__compactPriceRefresh = () => {
    if (!callbacks.size) throw new Error('Current Prices minute refresh is not registered');
    for (const callback of callbacks.values()) callback();
  };
});
const page = await context.newPage();
page.setDefaultTimeout(10000);
page.setDefaultNavigationTimeout(12000);
page.on('pageerror', error => errors.push(error.message));
const main = () => page.locator('.market-price-summary').filter({has: page.locator('.price-option-select')});
const selection = () => main().locator('.price-option-select');
const displayed = () => main().locator('.price-option');
const shares = async scope => {
  const href = await scope.getByRole('link', {name: 'Share on WhatsApp', exact: true}).getAttribute('href');
  return new URL(href).searchParams.get('text');
};
const expectSelection = async (id, low) => {
  await page.waitForFunction(id => document.querySelector('.price-option-select')?.value === String(id), id);
  assert.equal(await selection().inputValue(), String(id));
  if (low !== undefined) await displayed().locator('.price-range').filter({hasText: low.toLocaleString('en-NG')}).waitFor();
};
const refresh = async () => {
  const response = page.waitForResponse(response => new URL(response.url()).pathname === '/api/price-updates');
  await page.evaluate(() => window.__compactPriceRefresh());
  assert.equal((await response).status(), 200);
};
const setPreference = async (prefix, enabled) => {
  const button = page.getByRole('button', {name: new RegExp(`^${prefix}:`)});
  if (/On/.test(await button.innerText()) !== enabled) await button.click();
};

try {
  await page.goto(origin + '/__test__/status');
  const status = await page.evaluate(() => fetch('/__test__/status').then(response => response.json()));
  assert.equal(status.synthetic_only, true);
  assert.equal(status.providers, 'disabled');
  const original = await page.evaluate(() => fetch('/api/price-updates').then(response => response.json()));
  const base = original[0];
  assert.ok(base?.commodity_id && base?.market_id);
  const price = (id, changes = {}) => ({...base, id,
    price_low: 40000 + id, price_high: 43000 + id, average_price: null,
    unit: '1 recorded container', bag_size: `Recorded size ${id}`,
    commodity_type: 'Recorded grade', notes: `Fabricated note ${id}`,
    update_date_time: '2026-06-01T10:00:00Z', ...changes});
  const old = price(1001, {bag_size: '25 litre jerrican'});
  const newer = price(1002, {bag_size: '25 liter jerican', update_date_time: '2026-06-10T10:00:00Z'});
  const tieLow = price(1003, {bag_size: '50L container', update_date_time: '2026-06-15T10:00:00Z'});
  const unconfirmed = price(1004, {bag_size: null, commodity_type: null, update_date_time: 'Unconfirmed date'});
  const latest = price(1005, {unit: 'Litre', bag_size: '25L jerrican',
    commodity_type: 'Highest recorded grade', update_date_time: '2026-06-15T10:00:00Z',
    notes: 'Market update: Fabricated stock notice for this recorded option.', possible_meaning: 'Do not publish this guidance as a public notice'});
  // Matching names must never collapse distinct saved IDs.
  const anotherMarket = price(1010, {market_id: 9002, market: {...base.market, id: 9002}});
  const anotherCommodity = price(1020, {commodity_id: 9003, commodity: {...base.commodity, id: 9003}});
  let currentRows = [old, tieLow, anotherMarket, unconfirmed, latest, newer, anotherCommodity];
  const historyRows = [price(900, {bag_size: '25 litre jerrican', update_date_time: '2026-05-01T10:00:00Z'}),
    old, newer, tieLow, unconfirmed, latest];
  const historyBefore = JSON.stringify(historyRows);
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates', route => {
    currentRequests++; return route.fulfill({json: currentRows});
  });
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => {
    historyRequests++; return route.fulfill({json: historyRows});
  });

  await page.goto(origin + '/prices');
  await expectSelection(latest.id, latest.price_low);
  await page.getByRole('heading', {name: 'Search commodity prices', exact: true}).waitFor();
  assert.equal(await page.locator('#price-search').getByRole('button', {name: 'Search prices', exact: true}).isEnabled(), true);
  assert.equal(await page.locator('#price-search select').nth(2).inputValue(), '');
  assert.match(await page.locator('.header-search-link').innerText(), /Search\s+prices/);
  checks.clear_search_heading_action_and_optional_movement_keep_existing_header_shortcut = true;
  assert.equal(await page.locator('.commodity-price-card').count(), 2);
  assert.equal(await page.locator('.commodity-price-card .commodity-image').count(), 2);
  assert.equal(await page.locator('.market-price-summary').count(), 3);
  assert.equal(await page.locator('.price-option').count(), 3);
  assert.equal(await page.locator('.price-option-select').count(), 1);
  assert.equal(await main().locator('.price-option').count(), 1);
  const options = await selection().locator('option').evaluateAll(nodes => nodes.map(option =>
    ({value: option.value, text: option.textContent})));
  assert.deepEqual(options.map(option => Number(option.value)).sort((a, b) => a - b),
    [1001, 1002, 1003, 1004, 1005]);
  assert.match(options.find(option => option.value === '1001').text, /25 litre jerrican/);
  assert.match(options.find(option => option.value === '1002').text, /25 liter jerican/);
  assert.match(options.find(option => option.value === '1005').text, /Highest recorded grade/);
  assert.equal(await selection().getAttribute('aria-label') === 'Size / grade' ||
    await selection().evaluate(node => [...node.labels].some(label => /Size \/ grade/.test(label.textContent))), true);
  checks.one_newest_summary_per_market_with_raw_alternatives_and_one_photo_per_commodity = true;
  checks.distinct_commodity_and_market_ids_not_names_and_singleton_has_no_selector = true;
  const notice = () => displayed().getByRole('complementary', {name: 'Market update', exact: true});
  assert.equal(await notice().count(), 1);
  assert.match(await notice().innerText(), /Fabricated stock notice for this recorded option/);
  assert.equal(await notice().locator('time').getAttribute('datetime'), latest.update_date_time);
  assert.match(await notice().locator('time').innerText(), /WAT/);
  assert.equal((await displayed().innerText()).includes(latest.possible_meaning), false);
  assert.equal(await displayed().locator('.price-card-note').count(), 0);
  await selection().selectOption(String(newer.id));
  await expectSelection(newer.id);
  assert.equal(await notice().count(), 0);
  assert.match(await displayed().locator('.price-card-note').innerText(), /Fabricated note 1002/);
  await selection().selectOption(String(latest.id));
  await expectSelection(latest.id);
  checks.explicit_public_market_note_uses_record_report_date_without_duplicate_note_or_guidance = true;

  // The old homepage sliced the first three records and repeated a commodity's
  // photo, hiding a different commodity farther down the current response.
  await page.goto(origin + '/');
  await expectSelection(latest.id, latest.price_low);
  assert.equal(await page.locator('.commodity-price-card').count(), 2);
  assert.equal(await page.locator('.commodity-price-card .commodity-image').count(), 2);
  assert.equal(await page.locator('.market-price-summary').count(), 3);
  assert.equal(await selection().locator('option').count(), 5);
  const homeIncoming = price(1099, {bag_size: 'New homepage size', update_date_time: '2026-06-19T10:00:00Z'});
  currentRows = [...currentRows, homeIncoming];
  await refresh();
  await expectSelection(homeIncoming.id, homeIncoming.price_low);
  await selection().selectOption(String(old.id));
  await expectSelection(old.id, old.price_low);
  assert.match(await shares(displayed()), /pu=1001/);
  await refresh();
  await expectSelection(old.id, old.price_low);
  currentRows = currentRows.filter(item => item.id !== homeIncoming.id);
  for (const width of [375, 1366]) {
    await page.setViewportSize({width, height: 900});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    await page.locator('.commodity-price-card').first().screenshot({path: path.join(lab, `runtime/grouped-homepage-${width}.png`)});
  }
  checks.homepage_groups_full_response_without_duplicate_photos_or_hiding_other_commodity_ids = true;
  checks.homepage_options_share_and_refresh_follow_selected_record_and_fit_mobile = true;
  await page.goto(origin + '/prices');
  await expectSelection(latest.id);

  assert.equal(await page.getByRole('link', {name: 'View history', exact: true}).count(), 0);
  assert.equal(await page.locator('.price-option').getByRole('link', {name: 'View price history', exact: true}).count(), 3);
  assert.equal(await displayed().getByRole('link', {name: 'View price history', exact: true}).getAttribute('href'),
    `/history?commodity_id=${base.commodity_id}&market_id=${base.market_id}`);
  assert.match(await shares(displayed()), /pu=1005/);
  assert.match(await shares(displayed()), /41,005/);
  await displayed().getByRole('link', {name: 'View price history', exact: true}).click();
  await page.locator('.locked-panel').waitFor();
  assert.equal(historyRequests, 0);
  checks.explicit_history_label_routes_matching_ids_and_preserves_guest_access_gate = true;

  await page.goto(origin + '/prices');
  await expectSelection(latest.id);
  const incoming = price(1006, {bag_size: 'New recorded size', update_date_time: '2026-06-20T10:00:00Z'});
  currentRows = [incoming, ...currentRows];
  await refresh();
  await expectSelection(incoming.id, incoming.price_low);
  assert.match(await shares(displayed()), /pu=1006/);
  currentRows = currentRows.filter(item => item.id !== incoming.id);
  await refresh();
  await expectSelection(latest.id, latest.price_low);
  checks.unselected_default_follows_newest_record_on_silent_refresh = true;

  // The ticker and Current Prices both have existing minute refreshes. Allow
  // their controlled responses to settle before measuring user selection alone;
  // the local selector must not add a request of its own.
  await page.waitForLoadState('networkidle');
  const beforeSelection = currentRequests;
  await selection().focus();
  await selection().press('End');
  await selection().press('Enter');
  const keyboardSelected = await selection().inputValue();
  assert.notEqual(keyboardSelected, String(latest.id));
  assert.match(await shares(displayed()), new RegExp(`pu=${keyboardSelected}(?:$|[^0-9])`));
  await selection().selectOption(String(old.id));
  await expectSelection(old.id, old.price_low);
  assert.match(await displayed().innerText(), /25 litre jerrican/);
  assert.match(await displayed().innerText(), /Fabricated note 1001/);
  assert.match(await shares(displayed()), /pu=1001/);
  await page.waitForLoadState('networkidle');
  assert.equal(currentRequests, beforeSelection);
  checks.keyboard_and_selected_price_details_share_and_history_follow_the_visible_choice = true;

  currentRows = currentRows.map(item => item.id === old.id ? {...item, price_low: 51000, price_high: 53000,
    notes: 'Fresh fabricated correction 1001'} : item);
  await refresh();
  await expectSelection(old.id, 51000);
  await displayed().getByText('Fresh fabricated correction 1001', {exact: false}).waitFor();
  currentRows = [incoming, ...currentRows];
  await refresh();
  await expectSelection(old.id, 51000);
  assert.equal(await selection().locator('option').count(), 6);
  currentRows = currentRows.filter(item => item.id !== old.id);
  await refresh();
  await expectSelection(incoming.id, incoming.price_low);
  assert.match(await shares(displayed()), /pu=1006/);
  checks.silent_refresh_updates_chosen_record_keeps_existing_choice_and_recovers_removed_choice = true;

  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('trial@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  await page.goto(origin + '/prices');
  await expectSelection(incoming.id);
  let watchedBody;
  let flaggedId;
  await page.route(url => url.origin === origin && url.pathname === '/api/watchlist', async route => {
    assert.equal(route.request().method(), 'POST');
    watchedBody = route.request().postDataJSON();
    await route.fulfill({status: 201, json: {id: 1}});
  });
  await page.route(url => url.origin === origin && /^\/api\/price-updates\/\d+\/flag$/.test(url.pathname), async route => {
    assert.equal(route.request().method(), 'POST');
    flaggedId = Number(new URL(route.request().url()).pathname.match(/\/(\d+)\/flag$/)[1]);
    await route.fulfill({status: 201, json: {id: 1}});
  });
  await selection().selectOption(String(newer.id));
  await displayed().getByRole('button', {name: /Get price alerts/}).click();
  await displayed().getByRole('button', {name: /Alerts on/}).waitFor();
  assert.deepEqual(watchedBody, {commodity_id: base.commodity_id, market_id: base.market_id});
  await displayed().getByRole('button', {name: /Report wrong price/}).click();
  await displayed().getByRole('button', {name: /Reported/}).waitFor();
  assert.equal(flaggedId, newer.id);
  await selection().selectOption(String(latest.id));
  assert.equal(await displayed().getByRole('button', {name: /Get price alerts/}).isEnabled(), true);
  assert.equal(await displayed().getByRole('button', {name: /Report wrong price/}).isEnabled(), true);
  const secondMarket = page.locator('.market-price-summary').filter({has:
    page.locator(`a[href="/history?commodity_id=${base.commodity_id}&market_id=9002"]`)});
  assert.equal(await secondMarket.count(), 1);
  assert.match(await shares(secondMarket), /pu=1010/);
  await secondMarket.getByRole('button', {name: /Get price alerts/}).click();
  await secondMarket.getByRole('button', {name: /Alerts on/}).waitFor();
  assert.deepEqual(watchedBody, {commodity_id: base.commodity_id, market_id: 9002});
  checks.authenticated_watch_pair_and_flag_record_match_selection_without_leaking_previous_state = true;

  await displayed().getByRole('link', {name: 'View price history', exact: true}).click();
  await page.locator('.history-table-view tbody tr').nth(historyRows.length - 1).waitFor();
  assert.equal(await page.locator('.history-table-view tbody tr').count(), historyRows.length);
  assert.equal(await page.locator('.history-card-list > article').count(), historyRows.length);
  assert.equal(await page.getByRole('button', {name: 'All history', exact: true}).getAttribute('aria-pressed'), 'true');
  assert.equal(JSON.stringify(historyRows), historyBefore);
  checks.full_history_retains_all_current_and_older_records_in_table_and_mobile_cards = true;

  currentRows = [old, tieLow, anotherMarket, unconfirmed, latest, newer, anotherCommodity];
  await page.goto(origin + '/prices');
  await expectSelection(latest.id);
  await setPreference('Easy reading', true);
  for (const width of [375, 1366]) for (const dark of [true, false]) {
    await page.setViewportSize({width, height: 900});
    await setPreference('Dark mode', dark);
    await selection().selectOption(String(newer.id));
    await expectSelection(newer.id, newer.price_low);
    assert.equal(await page.locator('.price-option').count(), 3);
    const layout = await selection().evaluate(node => ({
      color: getComputedStyle(node).color,
      background: getComputedStyle(node).backgroundColor,
      documentFits: document.documentElement.scrollWidth <= innerWidth + 1,
      selectFits: node.scrollWidth <= node.clientWidth + 1,
      summaryFits: [...document.querySelectorAll('.market-price-summary')].every(item => item.scrollWidth <= item.clientWidth + 1),
      easyReading: document.documentElement.classList.contains('easy-reading'),
      theme: document.documentElement.dataset.theme,
    }));
    assert.equal(layout.documentFits, true, `No page overflow at ${width}, dark ${dark}`);
    assert.equal(layout.selectFits, true);
    assert.equal(layout.summaryFits, true);
    assert.equal(layout.easyReading, true);
    assert.equal(layout.theme, dark ? 'dark' : 'light');
    assert.notEqual(layout.color, layout.background);
    assert.notEqual(layout.color, 'rgba(0, 0, 0, 0)');
    await selection().selectOption(String(latest.id));
    const noteLayout = await notice().evaluate(node => {
      const luminance = color => {
        const channels = color.match(/[\d.]+/g).slice(0, 3).map(value => {
          const channel = Number(value) / 255;
          return channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4;
        });
        return channels[0] * .2126 + channels[1] * .7152 + channels[2] * .0722;
      };
      const background = luminance(getComputedStyle(node).backgroundColor);
      const contrast = element => {
        const foreground = luminance(getComputedStyle(element).color);
        return (Math.max(foreground, background) + .05) / (Math.min(foreground, background) + .05);
      };
      return {bodyContrast: contrast(node), dateContrast: contrast(node.querySelector('.market-update-date')),
        fits: node.scrollWidth <= node.clientWidth + 1};
    });
    assert.ok(noteLayout.bodyContrast >= 4.5);
    assert.ok(noteLayout.dateContrast >= 4.5);
    assert.equal(noteLayout.fits, true);
    Object.assign(layout, {marketUpdate: noteLayout});
    geometry.push({width, dark, ...layout});
    if (dark) await page.locator('.commodity-price-card').first().screenshot({
      path: path.join(lab, `runtime/compact-current-prices-${width}.png`)});
  }
  checks.compact_prices_keyboard_mobile_and_both_themes_fit_with_easy_reading = true;
  assert.deepEqual(errors, []);
  assert.equal(outside, 0);
} catch (error) {
  failure = error;
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry,
    synthetic_only: true, production_connections: 0, provider_calls: 0,
    api_writes: 'Only intercepted synthetic watch/flag responses; login uses guarded local account',
    external_page_requests: outside, current_requests: currentRequests, history_requests: historyRequests,
    browser_errors: errors, failure: failure ? String(failure.stack || failure) : null};
  fs.writeFileSync(path.join(lab, 'runtime/compact-current-prices-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
  await browser.close();
}
if (failure) throw failure;
