import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)), origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
let outside=0;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
try{
  await page.goto(origin+'/login');
  const identity=await page.evaluate(()=>fetch('/__test__/status').then(r=>r.json()));
  assert.equal(identity.synthetic_only,true);assert.equal(identity.providers,'disabled');
  await page.getByLabel('Email',{exact:true}).fill('admin@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const cookie=(await context.cookies()).find(item=>item.name==='priceyard_local_session');
  assert.ok(cookie);assert.equal(cookie.httpOnly,true);assert.equal(cookie.sameSite,'Lax');
  const storage=await page.evaluate(()=>({local:localStorage.getItem('priceyard_access_token'),session:sessionStorage.getItem('priceyard_access_token')}));
  assert.deepEqual(storage,{local:null,session:null});
  await page.goto(origin+'/admin');await page.waitForFunction(()=>document.querySelectorAll('.admin-metric').length===14);
  const sample=await page.evaluate(async()=>{
    const results={};
    const start=performance.now();
    for(const endpoint of ['/health','/price-updates','/admin/summary']){
      const timings=[];
      for(let index=0;index<8;index++){
        if(performance.now()-start>20000)throw Error('Serial performance budget exceeded');
        const before=performance.now(), response=await fetch('/api'+endpoint,{signal:AbortSignal.timeout(3000)});
        if(response.status!==200)throw Error('Synthetic read failed');
        await response.arrayBuffer();timings.push(performance.now()-before);
      }
      timings.sort((a,b)=>a-b);const round=n=>Math.round(n*100)/100;
      results[endpoint]={requests:timings.length,median_ms:round(timings[4]),p95_ms:round(timings[7]),max_ms:round(timings[7])};
    }
    return {results,elapsed_ms:Math.round(performance.now()-start),web_locks:!!navigator.locks,secure_context:window.isSecureContext};
  });
  await page.setViewportSize({width:375,height:812});
  assert.equal(await page.locator('.admin-metric').count(),14);
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth>innerWidth+1),false);
  assert.equal(outside,0);
  const value={passed:true,profile:'isolated loopback HTTP rehearsal; not hosted staging',chromium_version:browser.version(),
    original_admin_cards:14,mobile_width:375,http_only_cookie:true,javascript_bearer_storage_absent:true,
    browser_secure_context:sample.secure_context,web_locks_available:sample.web_locks,tls_verified:false,
    serial_requests:24,concurrency:1,performance_sample:sample,production_capacity_or_slo_proven:false,
    google_provider_verified:false,paystack_test_mode_verified:false,external_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'evidence/batch-84-browser-performance.json'),JSON.stringify(value,null,2));console.log(JSON.stringify(value));
}finally{await browser.close();}
