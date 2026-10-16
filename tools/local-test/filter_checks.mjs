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
async function fixture(){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>{
  localStorage.setItem('priceyard_onboarding_seen','1');
  const interval=window.setInterval.bind(window),clear=window.clearInterval.bind(window);window.__refreshCallbacks=new Map();
  window.setInterval=(callback,delay,...args)=>{const id=interval(callback,delay,...args);if(delay===60000)window.__refreshCallbacks.set(id,()=>callback(...args));return id;};
  window.clearInterval=id=>{window.__refreshCallbacks.delete(id);return clear(id);};
  const fetch=window.fetch.bind(window);window.__downStarted=0;window.__priceStarted=0;window.__priceFinished=0;
  window.fetch=async(input,...args)=>{const url=new URL(typeof input==='string'?input:input.url,location.href);const prices=url.pathname==='/api/price-updates';if(prices){window.__priceStarted++;if(url.searchParams.get('movement')==='down')window.__downStarted++;}const response=await fetch(input,...args);if(prices){await response.clone().arrayBuffer();window.__priceFinished++;}return response;};
 });
 const page=await context.newPage();page.setDefaultTimeout(15000);await page.goto(origin+'/prices');
 await page.locator('.price-card').first().waitFor();await page.waitForLoadState('networkidle');
 const prices=await page.evaluate(()=>fetch('/api/price-updates').then(r=>r.json()));
 assert.equal(prices.length,1);assert.equal(prices[0].movement,'up');return {context,page,prices};
}
async function tick(page){await page.evaluate(()=>{for(const callback of window.__refreshCallbacks.values())callback();});}
async function settled(page){
 // networkidle is a one-time load milestone, not a wait for later refreshes.
 await page.waitForFunction(()=>window.__priceStarted===window.__priceFinished);
 await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
}
try {
 {
  const {context,page,prices}=await fixture(),ready=deferred(),release=deferred();
  // Layout's ticker and the price list both refresh. Hold both requests before
  // applying a filter, otherwise the checker can race the second request itself.
  let held=0;
  await context.route('**/api/price-updates',async route=>{if(++held===2)ready.resolve();await release.promise;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(prices)});});
  await tick(page);await ready.promise;
  await page.locator('.filter-bar select').nth(2).selectOption('down');await page.getByRole('button',{name:'Apply',exact:true}).click();
  await page.getByText(/No current prices found/).waitFor();release.resolve();await settled(page);
  checks.older_refresh_cannot_replace_applied_filter=await page.locator('.price-card').count()===0;
  await context.close();
 }
 {
  const {context,page}=await fixture();await page.locator('.filter-bar select').nth(2).selectOption('down');
  await tick(page);await settled(page);
  checks.draft_filter_waits_for_apply=await page.locator('.price-card').count()===1;
  await context.close();
 }
 {
  const {context,page}=await fixture(),ready=deferred(),release=deferred();
  await context.route('**/api/price-updates?movement=down',async route=>{ready.resolve();await release.promise;await route.fulfill({status:200,contentType:'application/json',body:'[]'});});
  await page.locator('.filter-bar select').nth(2).selectOption('down');await page.getByRole('button',{name:'Apply',exact:true}).click();await ready.promise;
  await tick(page);const count=await page.evaluate(()=>window.__downStarted);
  release.resolve();await settled(page);
  checks.background_refresh_does_not_duplicate_foreground_request=count===1;
  checks.foreground_loading_finishes=await page.getByRole('button',{name:'Apply',exact:true}).isEnabled();
  await context.close();
 }
 assert.equal(outside,0);
 console.log(JSON.stringify({observed:checks}));
 for(const [name,value] of Object.entries(checks))assert.equal(value,name==='foreground_loading_finishes'?true:!expectBug,name);
 const report={checks,expected_original_bug:expectBug,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/filter-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
