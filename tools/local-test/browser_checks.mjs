import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
const recovery = path.join(root, '.git/priceyard-local-recovery-20261015/p00/runtime');
const { chromium } = await import(pathToFileURL(path.join(recovery, 'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const origin = 'http://127.0.0.1:55446';
const browser = await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context = await browser.newContext({serviceWorkers:'block',viewport:{width:1366,height:900}});
let externalBlocked = 0;
await context.route('**/*', route => {
  if (new URL(route.request().url()).origin !== origin) { externalBlocked++; return route.abort(); }
  return route.continue();
});
await context.addInitScript(() => localStorage.setItem('priceyard_onboarding_seen','1'));
const page = await context.newPage();
page.setDefaultTimeout(12000);
page.setDefaultNavigationTimeout(12000);
const result = {};
async function login(email) {
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:/^Welcome, Test /}).first().waitFor();
}
try {
  await page.goto(origin+'/');
  await page.getByRole('heading',{name:'Know the market before you buy or sell.'}).waitFor();
  await page.locator('.price-card').first().waitFor();
  assert.equal(await page.getByText(/Grade:|Grade not recorded/).count(),0);
  await page.screenshot({path:path.join(lab,'runtime/original-home.png'),fullPage:true});
  result.original_home_and_price_cards = true;
  const checks = await page.evaluate(async()=>{
    const status=await fetch('/__test__/status').then(r=>r.json());
    const prices=await fetch('/api/price-updates').then(r=>r.json());
    const history=await fetch('/api/price-updates/history');
    return {status,prices,history:history.status};
  });
  assert.equal(checks.status.synthetic_only,true);
  assert.equal(checks.prices.length,1);
  assert.equal(checks.prices[0].commodity.name,'Egusi');
  assert.equal(checks.prices[0].market.name,'Kwali Market');
  assert.equal(checks.prices[0].bag_size,null);
  assert.ok(!('grade' in checks.prices[0]));
  assert.ok(!('source_1' in checks.prices[0]));
  assert.equal(checks.history,401);
  result.real_api_synthetic_fixture_and_guest_boundary = true;
  await page.goto(origin+'/prices');
  await page.locator('.price-card').first().waitFor();
  await page.locator('.filter-bar select').nth(0).selectOption({label:'Egusi'});
  await page.locator('.filter-bar select').nth(1).selectOption({label:'Kwali Market'});
  await page.getByRole('button',{name:'Apply',exact:true}).click();
  await page.locator('.price-card').first().waitFor();
  result.original_price_filters = true;
  await login('trial@example.com');
  assert.ok((await page.locator('body').innerText()).includes('2,500'));
  assert.ok((await page.locator('body').innerText()).includes('6,000'));
  await page.goto(origin+'/history');
  await page.getByRole('heading',{name:/^Price history$/i}).waitFor();
  result.trial_login_plans_and_history = true;
  await page.getByRole('button',{name:'Log out',exact:true}).click();
  await login('admin@example.com');
  await page.goto(origin+'/admin/prices');
  await page.getByRole('heading',{name:/^Price updates$/i}).waitFor();
  assert.equal(await page.getByLabel(/grade/i).count(),0);
  await page.screenshot({path:path.join(lab,'runtime/original-admin-prices.png'),fullPage:true});
  result.original_admin_login_and_price_form = true;
  await page.setViewportSize({width:375,height:812});
  await page.goto(origin+'/prices');
  await page.locator('.price-card').first().waitFor();
  await page.screenshot({path:path.join(lab,'runtime/original-mobile.png'),fullPage:true});
  result.mobile_original_loaded = true;
  result.mobile_document_overflow = await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth);
  console.log(JSON.stringify({passed:Object.keys(result).filter(k=>result[k]===true).length,result,external_page_requests_blocked:externalBlocked,production_connections:0}));
  fs.writeFileSync(path.join(lab,'runtime/browser-baseline.json'),JSON.stringify({result,external_page_requests_blocked:externalBlocked,production_connections:0},null,2));
} catch (error) {
  await page.screenshot({path:path.join(lab,'runtime/browser-failure.png'),fullPage:true});
  console.log(JSON.stringify({completed:result,url:page.url()}));
  throw error;
} finally {
  await browser.close();
}
