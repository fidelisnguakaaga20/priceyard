import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
let outside=0;const checks={};
function deferred(){let resolve;return {promise:new Promise(done=>resolve=done),resolve:()=>resolve()};}
try {
  for(const screen of ['/','/prices']){
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
    await context.addInitScript(()=>{
      localStorage.setItem('priceyard_onboarding_seen','1');window.__refreshCallbacks=new Map();window.__priceStarted=0;window.__priceFinished=0;
      const interval=setInterval.bind(window),clear=clearInterval.bind(window);
      window.setInterval=(callback,delay,...args)=>{const id=interval(callback,delay,...args);if(delay===60000)window.__refreshCallbacks.set(id,()=>callback(...args));return id;};
      window.clearInterval=id=>{window.__refreshCallbacks.delete(id);return clear(id);};
      const nativeFetch=window.fetch.bind(window);
      window.fetch=async(input,...args)=>{const url=new URL(typeof input==='string'?input:input.url,location.href),price=url.pathname==='/api/price-updates';if(price)window.__priceStarted++;const response=await nativeFetch(input,...args);if(price){await response.clone().arrayBuffer();window.__priceFinished++;}return response;};
    });
    const page=await context.newPage();page.setDefaultTimeout(15000);const ready=deferred(),release=deferred();
    try {
      await page.goto(origin+screen);await page.locator('.price-card').first().waitFor();await page.waitForLoadState('networkidle');
      const prices=await page.evaluate(()=>fetch('/api/price-updates').then(response=>response.json()));let mode='hold',held=0,live=0;
      await page.route(origin+'/api/price-updates',async route=>{
        const cached=mode==='hold';if(cached){if(++held===2)ready.resolve();await release.promise;}else live++;
        await route.fulfill({json:prices,headers:cached?{'X-PriceYard-Cache':'saved','X-PriceYard-Saved-At':'2026-10-17T12:00:00.000Z'}:{}});
      });
      await page.evaluate(()=>{for(const callback of window.__refreshCallbacks.values())callback();});await ready.promise;
      mode='live';await page.evaluate(()=>{for(const callback of window.__refreshCallbacks.values())callback();});
      await page.waitForFunction(()=>window.__priceFinished===window.__priceStarted-2);assert.equal(live,2);
      release.resolve();await page.waitForFunction(()=>window.__priceStarted===window.__priceFinished);
      await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
      checks[(screen==='/'?'home':'prices')+'_old_cached_response_cannot_replace_new_fresh_state']=await page.locator('.saved-price-notice').count()===0;
      assert.ok(await page.locator('.price-card').count()>0);
    } finally {release.resolve();await context.close();}
  }
  assert.ok(Object.values(checks).every(Boolean));assert.equal(outside,0);
  const report={checks,passed:Object.keys(checks).length,ticker_and_page_both_exercised:true,production_connections:0,external_page_requests:outside};
  fs.writeFileSync(path.join(lab,'runtime/offline-race-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {await browser.close();}
