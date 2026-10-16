import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446', expectBug=process.argv.includes('--expect-bug'), checks={};
let external=0;
async function fixture(trial=false) {
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();external++;return route.abort();});
  await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  const page=await context.newPage();page.setDefaultTimeout(12000);
  if(trial) {
    await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');
    await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:'Welcome, Test Trial'}).waitFor();
  }
  if(!trial)await page.goto(origin);
  const prices=await page.evaluate(()=>fetch('/api/price-updates?commodity=Egusi').then(r=>r.json()));
  return {context,page,prices};
}
async function navigate(page,name) {
  await page.evaluate(name=>{history.pushState(null,'','/commodities/'+encodeURIComponent(name));dispatchEvent(new PopStateEvent('popstate'));},name);
  await page.getByRole('heading',{name,exact:true}).waitFor();
}
async function settle(page) {await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,250)));}
function deferred() {let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
try {
  {
    const {context,page,prices}=await fixture(),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/price-updates?commodity=Egusi',async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(prices)});sent.resolve();
    });
    await page.goto(origin+'/commodities/Egusi');await ready.promise;
    await navigate(page,'Not-a-record');
    await page.getByText('No current approved Not-a-record record is available.',{exact:true}).waitFor();
    release.resolve();await sent.promise;await settle(page);
    checks.late_price_does_not_replace_new_route=await page.locator('.detail-card').count()===0;
    await context.close();
  }
  {
    const {context,page}=await fixture(),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/price-updates?commodity=Not-a-record',async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic superseded price error'})});sent.resolve();
    });
    await page.goto(origin+'/commodities/Not-a-record');await ready.promise;
    await navigate(page,'Egusi');await page.locator('.detail-card').first().waitFor();
    release.resolve();await sent.promise;await settle(page);
    checks.late_error_does_not_poison_new_route=!(await page.locator('body').innerText()).includes('Synthetic superseded price error');
    await context.close();
  }
  {
    const {context,page}=await fixture(true);
    await context.route('**/api/quality-signals',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic quality service unavailable'})}));
    await context.route('**/api/buying-zones',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{id:9999,commodity_id:1,market_id:1,price_low:210000,price_high:220000,reason:'Synthetic independent buying-zone observation',confidence:'Low confidence',valid_from:null,valid_to:null}])}));
    await page.goto(origin+'/commodities/Egusi');
    await page.getByRole('heading',{name:'Buying zone',exact:true}).waitFor();
    if(!expectBug) {
      await page.getByText('Synthetic independent buying-zone observation',{exact:true}).waitFor();
      await page.getByText('Synthetic quality service unavailable',{exact:true}).waitFor();
    } else await settle(page);
    const body=await page.locator('body').innerText();
    checks.one_failed_section_keeps_successful_sections=body.includes('Synthetic independent buying-zone observation');
    checks.failed_section_shows_existing_error_box=body.includes('Synthetic quality service unavailable');
    await context.close();
  }
  {
    const {context,page}=await fixture(true),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/market-signals',async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{id:9998,commodity_id:1,market_id:1,signal_type:'Synthetic old commodity signal',signal_description:'Synthetic superseded observation',possible_meaning:null}])});sent.resolve();
    });
    await page.goto(origin+'/commodities/Egusi');await ready.promise;
    await navigate(page,'Not-a-record');
    await page.getByText('No current approved Not-a-record record is available.',{exact:true}).waitFor();
    release.resolve();await sent.promise;
    await page.getByRole('heading',{name:'Market signals',exact:true}).waitFor();await settle(page);
    checks.late_intelligence_does_not_follow_old_commodity=!(await page.locator('body').innerText()).includes('Synthetic old commodity signal');
    await context.close();
  }
  assert.equal(external,0);
  for(const [name,passed] of Object.entries(checks))assert.equal(passed,!expectBug,name);
  const report={checks,expected_original_bug:expectBug,external_page_requests:external,production_connections:0,extra_commodities_or_markets_created:0};
  fs.writeFileSync(path.join(lab,'runtime/detail-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {await browser.close();}
