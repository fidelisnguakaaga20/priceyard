import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab = path.dirname(fileURLToPath(import.meta.url)), origin = 'http://127.0.0.1:55446';
const recovery = path.resolve(lab, '../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium} = await import(pathToFileURL(path.join(recovery, 'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser = await chromium.launch({headless:true, args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context = await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()}, serviceWorkers:'block'});
let outside = 0;
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin === origin) return route.continue();
  outside++; return route.abort();
});
await context.addInitScript(() => localStorage.setItem('priceyard_onboarding_seen','1'));
const page = await context.newPage();
page.setDefaultTimeout(20000);
async function api(endpoint) {
  return page.evaluate(async endpoint => {
    const token = localStorage.getItem('priceyard_access_token');
    const response = await fetch('/api' + endpoint, {headers: token ? {Authorization:'Bearer ' + token} : {}});
    return {status:response.status, body:await response.json()};
  }, endpoint);
}
try {
  await page.goto(origin + '/prices');
  await page.locator('.price-card').first().waitFor();
  const publicPrices = await api('/price-updates');
  assert.equal(publicPrices.status,200);
  assert.ok(publicPrices.body.every(row => !('source_1' in row) && !('source_2' in row)));
  assert.equal((await api('/audit-logs')).status,401);
  await page.goto(origin + '/login');
  await page.getByLabel('Email',{exact:true}).fill('admin@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
  const logs = await api('/audit-logs');
  assert.equal(logs.status,200);
  const legacy = logs.body.find(row => row.action === 'local.synthetic_legacy');
  assert.ok(legacy);
  assert.deepEqual(legacy.old_value,{notes:'Retained synthetic audit evidence'});
  assert.deepEqual(legacy.new_value,{notes:'Retained synthetic audit evidence',nested:[{status:'approved'}]});
  assert.deepEqual((await api('/audit-logs/' + legacy.id)).body,legacy);
  const history = await api('/price-updates/history');
  assert.equal(history.status,200);
  assert.ok(history.body.every(row => !('source_1' in row) && !('source_2' in row)));
  const adminHistory = await api('/price-updates/admin/history');
  assert.equal(adminHistory.status,200);
  assert.ok(adminHistory.body.every(row => row.source_1 === 'LOCAL-PRIVATE-SOURCE'));
  await page.goto(origin + '/admin/audit');
  const row = page.locator('tbody tr').filter({hasText:'local.synthetic_legacy'});
  await row.waitFor();
  assert.match(await row.innerText(),/Retained synthetic audit evidence/);
  assert.match(await row.innerText(),/approved/);
  assert.doesNotMatch(await row.innerText(),/SYNTHETIC-LEGACY|source_[12]|password_hash|screenshot_data|access_token/i);
  assert.equal(outside,0);
  const report = {legacy_list_detail_and_original_audit_screen_redacted:true,retained_action_and_nonprivate_evidence:true,public_price_sources_hidden:true,legitimate_admin_price_sources_retained:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/audit-privacy-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {await browser.close();}
