import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug'),checks={};let outside=0;
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
async function fixture(trial=false){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(15000);
 if(trial){await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();}
 return {context,page};
}
async function navigate(page,search){await page.evaluate(search=>{history.pushState(null,'','/prices'+search);dispatchEvent(new PopStateEvent('popstate'));},search);}
async function settle(page){await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
try{
 {
  const {context,page}=await fixture();await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
  await navigate(page,'?commodity=Egusi&market=Kwali+Market');await settle(page);
  if(!expectBug)await page.waitForFunction(()=>document.querySelector('.filter-bar select')?.value==='Egusi');
  checks.navigation_updates_existing_filter_controls=(await page.locator('.filter-bar select').nth(0).inputValue())==='Egusi'&&(await page.locator('.filter-bar select').nth(1).inputValue())==='Kwali Market';
  await context.close();
 }
 {
  const {context,page}=await fixture(),ready=deferred(),release=deferred();
  await context.route('**/api/price-updates?commodity=Egusi',async route=>{ready.resolve();await release.promise;await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic obsolete URL error'})});});
  await page.goto(origin+'/prices?commodity=Egusi');await ready.promise;
  await navigate(page,'?commodity=Egusi&market=Kwali+Market');
  if(!expectBug)await page.locator('.price-card').first().waitFor();
  const response=page.waitForResponse(r=>r.url()===origin+'/api/price-updates?commodity=Egusi'&&r.status()===503);
  release.resolve();await response;await settle(page);
  checks.old_url_error_cannot_replace_new_navigation=await page.locator('.status-box.error').count()===0;
  await context.close();
 }
 for(const failure of [false,true]){
  const {context,page}=await fixture(true);await page.goto(origin+'/history');await page.locator('.history-table-view tbody tr').first().waitFor();
  const history=await page.evaluate(async()=>{const token=localStorage.getItem('priceyard_access_token');return fetch('/api/price-updates/history?commodity=Egusi',{headers:{Authorization:'Bearer '+token}}).then(r=>r.json());});
  const ready=deferred(),release=deferred();
  await context.route('**/api/price-updates/history?commodity=Egusi',async route=>{ready.resolve();await release.promise;await route.fulfill({status:failure?503:200,contentType:'application/json',body:JSON.stringify(failure?{detail:'Synthetic superseded history error'}:history)});});
  // Fault injection submits two native form events while the first is pending;
  // ordinary disabled buttons already prevent most accidental double-clicks.
  await page.locator('.filter-bar').evaluate(form=>form.requestSubmit());await ready.promise;
  await page.locator('.filter-bar select').nth(2).selectOption('morning');
  await page.locator('.filter-bar').evaluate(form=>form.requestSubmit());await page.getByText(/No history records found/).waitFor();
  const response=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/history?commodity=Egusi'&&r.status()===(failure?503:200));
  release.resolve();await response;await settle(page);
  checks[failure?'old_history_error_is_ignored':'old_history_rows_do_not_replace_latest_filters']=failure?await page.locator('.status-box.error').count()===0:await page.locator('.history-table-view tbody tr').count()===0;
  await context.close();
 }
 assert.equal(outside,0);for(const [name,value] of Object.entries(checks))assert.equal(value,!expectBug,name);
 const report={checks,expected_original_bug:expectBug,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/navigation-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
