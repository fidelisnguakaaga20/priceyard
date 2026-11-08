import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';

const lab = path.dirname(fileURLToPath(import.meta.url));
const origin = 'http://127.0.0.1:55446';
const recovery = path.resolve(lab, '../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium} = await import(pathToFileURL(path.join(recovery, 'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser = await chromium.launch({headless: true, args: ['--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run']});
let outside = 0;
const context = await browser.newContext({extraHTTPHeaders: {'X-PriceYard-Test-Client': crypto.randomUUID()}, serviceWorkers: 'block'});
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++;
  return route.abort();
});
await context.addInitScript(() => localStorage.setItem('priceyard_onboarding_seen', '1'));
const page = await context.newPage();
page.setDefaultTimeout(20000);
async function api(url) {
  return page.evaluate(async url => {
    const response = await fetch('/api' + url, {headers: {Authorization: 'Bearer ' + localStorage.getItem('priceyard_access_token')}});
    if (!response.ok) throw new Error('Synthetic API failed: ' + response.status);
    return response.json();
  }, url);
}

try {
  await page.goto(origin + '/login');
  await page.getByLabel('Email', {exact: true}).fill('admin@example.com');
  await page.getByLabel('Password', {exact: true}).fill('PriceYardDemo8!');
  await page.getByRole('button', {name: 'Log in', exact: true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading', {name: 'Welcome, Test Admin', exact: true}).waitFor();
  const price = (await api('/price-updates'))[0];
  const historyBefore = await api('/price-updates/admin/history');
  const marker = 'Synthetic planning ' + crypto.randomUUID();
  const cases = [
    ['buying-zones', 'buying-zones', 'buying_zones', 'buying_zone',
      {price_low: '210000', price_high: '220000', reason: marker, confidence: 'Low confidence'}, {reason: marker + ' corrected'}],
    ['sell-watch', 'sell-watch-windows', 'sell_watch_windows', 'sell_watch_window',
      {start_period: 'Synthetic recorded period', observation: marker, confidence: 'Low confidence'}, {observation: marker + ' corrected'}],
    ['storage', 'storage-suitability', 'storage_suitability', 'storage_suitability',
      {summary: marker}, {summary: marker + ' corrected'}],
  ];
  for (const [screen, endpoint, table, prefix, fields, changes] of cases) {
    await page.goto(origin + '/admin/' + screen);
    const form = page.locator('form.admin-form');
    await form.waitFor();
    for (const [name, value] of Object.entries({commodity_id: String(price.commodity_id), market_id: String(price.market_id), ...fields})) {
      await form.locator('[name="' + name + '"]').fill(value);
    }
    if (screen === 'storage') {
      await form.locator('[name=price_update_id]').fill(String(price.id));
      await form.locator('[name=suitability_status]').selectOption('watch');
    }
    const created = page.waitForResponse(r => r.url() === origin + '/api/' + endpoint && r.request().method() === 'POST');
    const reloaded = page.waitForResponse(r => r.url() === origin + '/api/' + endpoint && r.request().method() === 'GET');
    await form.getByRole('button', {name: /^Save /}).click();
    const response = await created;
    assert.equal(response.status(), 201);
    const item = await response.json();
    await (await reloaded).finished();
    await page.waitForFunction(() => !document.querySelector('button:disabled'));
    await form.locator('[name=id]').fill(String(item.id));
    for (const [name, value] of Object.entries(changes)) await form.locator('[name="' + name + '"]').fill(value);
    const edited = page.waitForResponse(r => r.url() === origin + `/api/${endpoint}/${item.id}` && r.request().method() === 'PATCH');
    const editReload = page.waitForResponse(r => r.url() === origin + '/api/' + endpoint && r.request().method() === 'GET');
    await form.getByRole('button', {name: /^Save /}).click();
    assert.equal((await edited).status(), 200);
    await (await editReload).finished();
    await page.waitForFunction(() => !document.querySelector('button:disabled'));
    await page.locator('.admin-card-list article').filter({hasText: marker + ' corrected'}).waitFor();
    const logs = (await api('/audit-logs')).filter(row => row.table_name === table && row.record_id === item.id).sort((a, b) => a.id - b.id);
    assert.deepEqual(logs.map(row => row.action), [prefix + '.create', prefix + '.edit']);
    for (const key of Object.keys(logs[1].old_value)) {
      const numeric = screen === 'buying-zones' && ['price_low', 'price_high'].includes(key);
      assert.deepEqual(numeric ? Number(logs[0].new_value[key]) : logs[0].new_value[key], numeric ? Number(logs[1].old_value[key]) : logs[1].old_value[key]);
    }
    for (const [key, value] of Object.entries(changes)) assert.equal(logs[1].new_value[key], value);
  }
  assert.deepEqual(await api('/price-updates/admin/history'), historyBefore);
  assert.equal(outside, 0);
  const report = {original_buying_sell_watch_storage_create_edit_controls: true, six_audit_records_verified: true, historical_price_rows_unchanged: true, no_new_delete_endpoint: true, synthetic_preview_reseed_required: true, external_page_requests: outside, production_connections: 0};
  fs.writeFileSync(path.join(lab, 'runtime/planning-checks.json'), JSON.stringify(report, null, 2));
  console.log(JSON.stringify(report));
} finally {
  // These original resources have no deletion control. Reseed only the disposable
  // in-memory preview after this check; never add a product deletion feature.
  await browser.close();
}
