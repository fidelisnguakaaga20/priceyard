// Focused serial synthetic checks; root runs through run_browser.py after building.
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
const checks = {}, geometry = [], contrast = [], errors = [];
let outside = 0, failure, page, context;
const contexts = [];
const newContext = async (prefs = {}, welcome = false) => {
  const current = await browser.newContext({serviceWorkers: 'block', hasTouch: true,
    viewport: {width: 375, height: 667}, reducedMotion: 'reduce',
    extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}});
  contexts.push(current);
  await current.route('**/*', route => {
    if (new URL(route.request().url()).origin === origin) return route.continue();
    outside++; return route.abort();
  });
  await current.addInitScript(({prefs, welcome}) => {
    localStorage.setItem('priceyard_data_saver', '1');
    if (!welcome) localStorage.setItem('priceyard_onboarding_seen', '1');
    localStorage.setItem('priceyard_easy_reading', prefs.easy ? '1' : '0');
    localStorage.setItem('priceyard_dark_mode', prefs.dark ? '1' : '0');
  }, {prefs, welcome});
  return current;
};
const attachPage = async current => {
  const p = await current.newPage();
  p.setDefaultTimeout(10000); p.setDefaultNavigationTimeout(12000);
  p.on('pageerror', error => errors.push(error.message));
  return p;
};
const contrastState = async locator => locator.evaluate(node => {
  const rgb = value => (value.match(/[\d.]+/g) || []).map(Number);
  const blend = (foreground, background) => {
    const alpha = foreground[3] ?? 1;
    return foreground.slice(0, 3).map((value, index) => value * alpha + background[index] * (1 - alpha));
  };
  const background = element => {
    if (!element) return [255, 255, 255];
    const color = rgb(getComputedStyle(element).backgroundColor);
    return blend(color, (color[3] ?? 1) === 1 ? [255, 255, 255] : background(element.parentElement));
  };
  const luminance = channels => channels.map(channel => channel / 255)
    .map(channel => channel <= .04045 ? channel / 12.92 : ((channel + .055) / 1.055) ** 2.4)
    .reduce((total, channel, index) => total + channel * [.2126, .7152, .0722][index], 0);
  const style = getComputedStyle(node), bg = background(node);
  const light = [luminance(blend(rgb(style.color), bg)), luminance(bg)].sort((a, b) => b - a);
  return {text: node.textContent.trim(), ratio: (light[0] + .05) / (light[1] + .05),
    color: style.color, background: bg, fontSize: parseFloat(style.fontSize),
    lineHeight: parseFloat(style.lineHeight), fontWeight: Number(style.fontWeight)};
});
const preference = async (prefix, enabled) => {
  const button = page.getByRole('button', {name: new RegExp(`^${prefix}:`)});
  if (/On/.test(await button.innerText()) !== enabled) await button.click();
};
const shortcut = () => page.locator('.header-inner').getByRole('link', {name: 'Search prices', exact: true});
const expectSearchFocus = async () => {
  await page.waitForFunction(() => {
    const form = document.querySelector('#price-search');
    const select = form?.querySelector('select');
    const header = document.querySelector('.site-header')?.getBoundingClientRect();
    if (!form || !select || !header) return false;
    const rect = form.getBoundingClientRect();
    return document.activeElement === select && rect.top >= header.bottom - 2 && rect.top <= header.bottom + 45;
  });
};
try {
  // Fresh visitors see a genuinely readable introduction in every preference combination.
  for (const easy of [false, true]) for (const dark of [false, true]) {
    const welcomeContext = await newContext({easy, dark}, true);
    const welcomePage = await attachPage(welcomeContext);
    page = welcomePage;
    await page.goto(origin + '/');
    const dialog = page.getByRole('dialog', {name: 'Welcome to PriceYard', exact: true});
    await dialog.waitFor();
    const paragraph = await contrastState(dialog.locator('#priceyard-onboarding-step'));
    const heading = await contrastState(dialog.getByRole('heading'));
    assert.ok(paragraph.ratio >= 4.5, JSON.stringify({easy, dark, paragraph}));
    assert.ok(heading.ratio >= 4.5, JSON.stringify({easy, dark, heading}));
    assert.ok(paragraph.fontSize >= 16 && paragraph.lineHeight >= paragraph.fontSize * 1.5);
    for (const button of await dialog.getByRole('button').all()) {
      const state = await contrastState(button);
      assert.ok(state.ratio >= 4.5, JSON.stringify({easy, dark, state}));
    }
    contrast.push({control: 'welcome', easy, dark, paragraph, heading});
    assert.equal(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth + 1), false);
    const skip = dialog.getByRole('button', {name: 'Skip', exact: true});
    await skip.focus(); await page.keyboard.press('Shift+Tab');
    assert.equal(await dialog.getByRole('button', {name: 'Next', exact: true}).evaluate(node => node === document.activeElement), true);
    await page.keyboard.press('Tab');
    assert.equal(await skip.evaluate(node => node === document.activeElement), true);
    await dialog.getByRole('button', {name: 'Next', exact: true}).click();
    await dialog.getByRole('button', {name: 'Back', exact: true}).click();
    assert.match(await dialog.getByRole('heading').innerText(), /1\/4/);
    if (dark && easy) await page.screenshot({path: path.join(runtime, 'discovery-welcome-dark-mobile.png'), fullPage: false});
    await page.keyboard.press('Escape'); await dialog.waitFor({state: 'hidden'});
    assert.equal(await page.evaluate(() => localStorage.getItem('priceyard_onboarding_seen')), '1');
    assert.equal(await page.locator('.brand').evaluate(node => node === document.activeElement), true);
    await welcomeContext.close();
  }
  checks.welcome_readable_in_both_themes_and_easy_reading_without_the_shared_dark_card_conflict = true;
  checks.welcome_keyboard_focus_trap_navigation_dismissal_and_focus_return_preserved = true;

  const firstSearchContext = await newContext({}, true);
  page = await attachPage(firstSearchContext);
  await page.goto(origin + '/prices#price-search');
  const firstSearchDialog = page.getByRole('dialog', {name: 'Welcome to PriceYard', exact: true});
  await firstSearchDialog.waitFor();
  await page.waitForFunction(() => {
    const commoditySelect = document.querySelector('#price-search select');
    return commoditySelect && commoditySelect.options.length > 1
      && document.querySelector('#price-search button[type=submit]')?.disabled === false;
  });
  await page.evaluate(() => new Promise(resolve => requestAnimationFrame(() => requestAnimationFrame(resolve))));
  assert.equal(await firstSearchDialog.evaluate(node => node.contains(document.activeElement)), true);
  await firstSearchDialog.getByRole('button', {name: 'Skip', exact: true}).click();
  await firstSearchDialog.waitFor({state: 'hidden'});
  await expectSearchFocus();
  checks.first_visit_hashed_search_waits_for_welcome_dismissal_before_focusing_filters = true;
  await firstSearchContext.close();

  context = await newContext(); page = await attachPage(context);
  await page.goto(origin + '/__test__/status');
  assert.equal((await page.evaluate(() => fetch('/__test__/status').then(r => r.json()))).synthetic_only, true);
  const originals = await page.evaluate(() => fetch('/api/price-updates').then(r => r.json()));
  const base = originals[0]; assert.ok(base?.commodity?.id && base?.market?.id);
  const commodities = [{...base.commodity, name: 'Synthetic duplicate commodity', is_upcoming: false},
    {...base.commodity, id: 99111, name: 'Synthetic duplicate commodity', is_upcoming: false},
    {...base.commodity, id: 99112, name: 'Synthetic upcoming commodity', is_upcoming: true}];
  const markets = [{...base.market, name: 'Synthetic duplicate market'},
    {...base.market, id: 99113, name: 'Synthetic duplicate market'},
    {...base.market, id: 99114, name: 'Synthetic unmatched market'}];
  const rows = [0, 1].map(index => ({...base, id: 99120 + index,
    commodity: commodities[index], commodity_id: commodities[index].id,
    market: markets[index], market_id: markets[index].id,
    price_low: 40000 + index * 1000, price_high: 43000 + index * 1000}));
  const requests = {commodities: 0, markets: 0, history: 0}, priceQueries = [];
  let catalogMode = 'normal', releaseCatalogs;
  let catalogGate = Promise.resolve();
  for (const [endpoint, records] of [['commodities', commodities], ['markets', markets]]) {
    await page.route(url => url.origin === origin && url.pathname === `/api/${endpoint}`, async route => {
      requests[endpoint]++;
      if (catalogMode === 'slow') await catalogGate;
      if (catalogMode === 'failed' && endpoint === 'markets')
        return route.fulfill({status: 503, json: {detail: 'Synthetic unavailable market list'}});
      return route.fulfill({json: records});
    });
  }
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates', route => {
    const query = new URL(route.request().url()).searchParams; priceQueries.push(query.toString());
    if (catalogMode === 'failed-prices') return route.fulfill({status: 503, json: {detail: 'Synthetic unavailable price registrations'}});
    if (catalogMode === 'empty-prices') return route.fulfill({json: []});
    return route.fulfill({json: rows.filter(row => (!query.has('commodity_id') || String(row.commodity_id) === query.get('commodity_id'))
      && (!query.has('market_id') || String(row.market_id) === query.get('market_id')))});
  });
  await page.route(url => url.origin === origin && url.pathname === '/api/price-updates/history', route => {
    requests.history++; return route.fulfill({json: []});
  });
  await page.goto(origin + '/');
  const home = () => page.getByRole('search', {name: 'Search current prices', exact: true});
  await page.waitForFunction(() => { const button = document.querySelector('.home-price-search button[type=submit]'); return button && !button.disabled; });
  assert.equal(requests.commodities, 1); assert.equal(requests.markets, 1);
  assert.equal(await home().locator('select').nth(0).locator('option').count(), 3);
  assert.equal(await home().locator('select').nth(1).locator('option').count(), 4);
  assert.equal(await shortcut().getAttribute('href'), '/prices#price-search');
  const nav = page.getByRole('navigation', {name: 'Primary navigation', exact: true});
  assert.equal(await nav.isVisible(), false); assert.equal(await shortcut().isVisible(), true);
  checks.homepage_search_is_visible_outside_the_menu_and_reuses_existing_catalog_requests = true;

  assert.equal(await home().locator('select').nth(0).locator('option').first().innerText(), 'Choose a commodity');
  assert.equal(await home().locator('select').nth(1).locator('option').first().innerText(), 'Choose a market');
  await home().locator('select').nth(0).selectOption(`id:${commodities[0].id}`);
  assert.deepEqual(await home().locator('select').nth(1).locator('option').evaluateAll(nodes => nodes.map(n => n.value)), ['', `id:${markets[0].id}`]);
  await home().locator('select').nth(1).selectOption(`id:${markets[0].id}`);
  await home().locator('select').nth(0).selectOption(`id:${commodities[1].id}`);
  assert.equal(await home().locator('select').nth(1).inputValue(), '');
  assert.deepEqual(await home().locator('select').nth(1).locator('option').evaluateAll(nodes => nodes.map(n => n.value)), ['', `id:${markets[1].id}`]);
  checks.homepage_choose_labels_and_registered_markets_match_exact_commodity_ids = true;
  checks.homepage_changing_commodity_clears_incompatible_market_even_with_duplicate_names = true;
  await home().locator('select').nth(1).selectOption(`id:${markets[1].id}`);
  await home().getByRole('button', {name: 'Search prices', exact: true}).click();
  await page.waitForURL(origin + `/prices?commodity_id=${commodities[1].id}&market_id=${markets[1].id}#price-search`);
  await expectSearchFocus();
  assert.equal(await page.locator('#price-search select').nth(0).inputValue(), `id:${commodities[1].id}`);
  assert.equal(await page.locator('#price-search select').nth(1).inputValue(), `id:${markets[1].id}`);
  await page.locator('.price-option').waitFor();
  assert.ok(priceQueries.some(query => new URLSearchParams(query).get('commodity_id') === String(commodities[1].id)
    && new URLSearchParams(query).get('market_id') === String(markets[1].id)));
  checks.homepage_search_uses_exact_ids_even_when_commodity_and_market_names_are_duplicates = true;

  // Preserve existing explicit bookmarks with honest empty results. The Home
  // dropdown itself no longer offers unrelated market combinations.
  await page.goto(origin + `/prices?commodity_id=${commodities[0].id}&market_id=${markets[2].id}#price-search`);
  await expectSearchFocus();
  const emptyResult = page.locator('.status-box').filter({hasText: 'No current prices found'});
  await emptyResult.waitFor();
  assert.match(await emptyResult.innerText(), /Synthetic duplicate commodity/);
  assert.match(await emptyResult.innerText(), /Synthetic unmatched market/);
  assert.equal(await page.locator('#price-search select').nth(0).inputValue(), `id:${commodities[0].id}`);
  assert.equal(await page.locator('#price-search select').nth(1).inputValue(), `id:${markets[2].id}`);
  assert.equal(await page.locator(`#price-search select option[value="id:${markets[2].id}"]`).count(), 1);
  assert.equal(await page.locator('.price-option').count(), 0);
  assert.ok(priceQueries.some(query => new URLSearchParams(query).get('commodity_id') === String(commodities[0].id)
    && new URLSearchParams(query).get('market_id') === String(markets[2].id)));
  checks.explicit_valid_market_without_current_prices_stays_selected_with_an_honest_empty_result = true;

  await page.evaluate(() => scrollTo(0, document.body.scrollHeight));
  await shortcut().click(); await page.waitForURL(origin + '/prices#price-search'); await expectSearchFocus();
  await page.evaluate(() => scrollTo(0, document.body.scrollHeight));
  await shortcut().click(); await expectSearchFocus();
  checks.header_search_reveals_and_focuses_filters_below_the_sticky_header_even_on_the_same_page = true;

  for (const selection of ['commodity', 'market', 'none']) {
    await page.goto(origin + '/'); await page.waitForFunction(() => { const button = document.querySelector('.home-price-search button[type=submit]'); return button && !button.disabled; });
    if (selection === 'commodity') await home().locator('select').nth(0).selectOption(`id:${commodities[0].id}`);
    if (selection === 'market') await home().locator('select').nth(1).selectOption(`id:${markets[0].id}`);
    await home().getByRole('button', {name: 'Search prices', exact: true}).click();
    await page.waitForURL(url => url.pathname === '/prices' && url.hash === '#price-search');
    const url = new URL(page.url());
    assert.equal(url.searchParams.get('commodity_id'), selection === 'commodity' ? String(commodities[0].id) : null);
    assert.equal(url.searchParams.get('market_id'), selection === 'market' ? String(markets[0].id) : null);
    await expectSearchFocus();
  }
  checks.optional_homepage_filters_preserve_commodity_only_market_only_and_all_prices_navigation = true;

  catalogMode = 'slow'; catalogGate = new Promise(resolve => { releaseCatalogs = resolve; });
  await page.goto(origin + '/'); await home().waitFor();
  assert.equal(await home().locator('select').nth(0).isDisabled(), true);
  assert.equal(await home().locator('select').nth(1).isDisabled(), true);
  assert.equal(await home().getByRole('button', {name: 'Search prices', exact: true}).isDisabled(), true);
  releaseCatalogs(); catalogMode = 'normal';
  await page.waitForFunction(() => { const button = document.querySelector('.home-price-search button[type=submit]'); return button && !button.disabled; });
  catalogMode = 'failed'; await page.goto(origin + '/');
  await home().locator('.home-search-status').waitFor();
  await page.waitForFunction(() => document.querySelector('.home-search-status')?.textContent.includes('could not be loaded'));
  assert.equal(await home().getByRole('button', {name: 'Search prices', exact: true}).isDisabled(), true);
  assert.equal(await home().getByRole('link', {name: 'Open current prices', exact: true}).getAttribute('href'), '/prices#price-search');
  catalogMode = 'normal';
  await shortcut().click(); await expectSearchFocus();
  checks.loading_and_failed_catalogs_do_not_submit_partial_searches_and_offer_existing_prices_fallback = true;

  catalogMode = 'failed-prices'; await page.goto(origin + '/');
  await page.waitForFunction(() => document.querySelector('.home-search-status')?.textContent.includes('could not be loaded'));
  assert.equal(await home().getByRole('button', {name: 'Search prices', exact: true}).isDisabled(), true);
  catalogMode = 'empty-prices'; await page.goto(origin + '/');
  await page.waitForFunction(() => { const button = document.querySelector('.home-price-search button[type=submit]'); return button && !button.disabled; });
  await home().locator('select').nth(0).selectOption(`id:${commodities[0].id}`);
  assert.equal(await home().locator('select').nth(1).locator('option').count(), 1);
  await home().getByText('No registered markets for this commodity yet.', {exact: true}).waitFor();
  checks.homepage_missing_price_registrations_cannot_offer_unrelated_markets = true;
  catalogMode = 'normal';

  await page.goto(origin + '/prices'); await page.locator('.price-option').first().waitFor();
  const ticker = page.locator('.price-ticker-track');
  await page.emulateMedia({reducedMotion: 'no-preference'}); await page.mouse.move(0, 650);
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationDuration), '56s');
  const pause = page.getByRole('button', {name: 'Pause scrolling', exact: true});
  await pause.click(); assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'paused');
  const before = await ticker.evaluate(node => getComputedStyle(node).transform);
  await page.waitForTimeout(120); assert.equal(await ticker.evaluate(node => getComputedStyle(node).transform), before);
  const resume = page.getByRole('button', {name: 'Resume scrolling', exact: true});
  assert.equal((await resume.innerText()).trim(), 'Resume');
  await resume.click(); assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationPlayState), 'running');
  await page.emulateMedia({reducedMotion: 'reduce'});
  assert.equal(await ticker.evaluate(node => getComputedStyle(node).animationName), 'none');
  checks.half_speed_ticker_preserves_pause_resume_and_reduced_motion = true;

  for (const account of ['guest', 'admin']) {
    if (account === 'admin') {
      await page.goto(origin + '/login');
      await page.getByLabel('Email', {exact: true}).fill('admin@example.com');
      await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
      await page.getByRole('button', {name: 'Log in', exact: true}).click(); await page.waitForURL('**/dashboard');
    }
    await page.goto(origin + '/prices');
    for (const width of [320, 375, 1366, 1441, 1920]) {
      await page.setViewportSize({width, height: width < 640 ? 667 : 900});
      for (const easy of [false, true]) for (const dark of [false, true]) {
        await preference('Easy reading', easy); await preference('Dark mode', dark);
        const menu = page.getByRole('button', {name: 'Toggle navigation', exact: true});
        const shape = await shortcut().evaluate(node => {
          const box = node.getBoundingClientRect(), brand = document.querySelector('.brand').getBoundingClientRect();
          return {left: box.left, right: box.right, width: box.width, height: box.height,
            overlapsBrand: box.left < brand.right && box.right > brand.left && box.top < brand.bottom && box.bottom > brand.top,
            overflow: document.documentElement.scrollWidth > innerWidth + 1};
        });
        assert.equal(shape.overflow, false); assert.equal(shape.overlapsBrand, false);
        assert.ok(shape.left >= 0 && shape.right <= width + 1 && shape.height >= 44);
        if (await menu.isVisible()) await menu.click();
        const current = page.getByRole('navigation', {name: 'Primary navigation', exact: true});
        await current.getByRole('link', {name: 'FAQ', exact: true}).waitFor();
        const navigationBounds = await current.locator('a, button').evaluateAll(nodes => nodes.map(node => {
          const rect = node.getBoundingClientRect();
          return {label: node.textContent.trim(), left: rect.left, right: rect.right};
        }));
        assert.ok(navigationBounds.every(box => box.left >= -1 && box.right <= width + 1),
          JSON.stringify({account, width, easy, dark, navigationBounds}));
        for (const text of ['Current Prices', 'FAQ', ...(account === 'admin' ? ['Admin', 'Dashboard'] : ['Log in'])]) {
          const state = await contrastState(current.getByRole('link', {name: text, exact: true}));
          assert.ok(state.ratio >= 4.5, JSON.stringify({account, width, easy, dark, state}));
          if (text === 'FAQ') assert.ok(state.fontWeight >= 600);
          contrast.push({control: 'menu', account, viewportWidth: width, easy, dark, ...state});
        }
        await current.getByRole('link', {name: 'FAQ', exact: true}).hover();
        assert.ok((await contrastState(current.getByRole('link', {name: 'FAQ', exact: true}))).ratio >= 4.5);
        if (await menu.isVisible()) { await page.keyboard.press('Escape'); assert.equal(await menu.getAttribute('aria-expanded'), 'false'); }
        geometry.push({control: 'header search', account, viewportWidth: width, easy, dark, ...shape, navigationBounds});
      }
    }
  }
  checks.header_search_and_all_menu_text_fit_guest_admin_mobile_desktop_themes_and_easy_reading = true;
  await page.goto(origin + '/');
  await home().waitFor();
  await page.setViewportSize({width: 375, height: 667});
  await page.screenshot({path: path.join(runtime, 'discovery-search-mobile.png'), fullPage: false});
  await page.getByRole('button', {name: 'Toggle navigation', exact: true}).click();
  await page.getByRole('navigation', {name: 'Primary navigation', exact: true}).getByRole('button', {name: 'Log out', exact: true}).click();
  await page.goto(origin + '/history'); await page.locator('.locked-panel').waitFor();
  assert.equal(await page.locator('.history-filters').count(), 0); assert.equal(requests.history, 0);
  checks.public_price_search_does_not_bypass_history_access_or_change_original_records = true;
  assert.deepEqual(errors, []); assert.equal(outside, 0);
} catch (error) {
  failure = error.stack || String(error);
  if (page && !page.isClosed()) await page.screenshot({path: path.join(runtime, 'discovery-readability-failure.png'), fullPage: false}).catch(() => {});
} finally {
  const report = {passed: Object.keys(checks).length, checks, geometry, contrast, failure,
    external_page_requests: outside, page_errors: errors, synthetic_only: true,
    production_connections: 0, production_records_changed: 0};
  fs.writeFileSync(path.join(runtime, 'discovery-readability-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify({...report, geometry: `${geometry.length} measurements in runtime report`,
    contrast: `${contrast.length} contrast checks in runtime report`}));
  for (const current of contexts) await current.close().catch(() => {});
  await browser.close();
  if (failure) process.exitCode = 1;
}
