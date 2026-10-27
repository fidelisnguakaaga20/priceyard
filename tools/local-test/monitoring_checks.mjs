import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
async function setOutage(enabled){assert.equal(await page.evaluate(async enabled=>(await fetch('/__test__/outage',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled})})).status,enabled),200);}
async function probe(){return page.evaluate(async()=>{
 const health=await fetch('/api/health',{credentials:'omit'}),prices=await fetch('/api/price-updates',{credentials:'omit'}),history=await fetch('/api/price-updates/history',{credentials:'omit'});
 const data=prices.ok?await prices.json():null;return {health:health.status,prices:prices.status,guest_history:history.status,public_sources_absent:data?data.every(row=>!('source_1' in row)&&!('source_2' in row)):null};
});}
try{
 await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();const normal=await probe();assert.deepEqual(normal,{health:200,prices:200,guest_history:401,public_sources_absent:true});
 await setOutage(true);const failed=await probe();assert.equal(failed.health,200);assert.equal(failed.prices,503);
 await page.reload();await page.locator('.status-box.error').waitFor();assert.equal(await page.locator('.price-card').count(),0);
 await setOutage(false);await page.getByRole('button',{name:'Search prices',exact:true}).click();await page.locator('.price-card').first().waitFor();assert.equal(await page.locator('.status-box.error').count(),0);
 const recovered=await probe();assert.deepEqual(recovered,normal);assert.equal(outside,0);
 const report={local_monitoring_drill_passed:true,liveness_does_not_mask_failed_price_read:true,normal,failed,recovered,original_error_apply_recovery:true,live_monitor_or_alerts_enabled:false,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/monitoring-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await setOutage(false).catch(()=>{});await browser.close();}
