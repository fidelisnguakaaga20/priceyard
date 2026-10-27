import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
let outside=0;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const result=await page.evaluate(async()=>{
  const token=localStorage.getItem('priceyard_access_token'),headers={Authorization:'Bearer '+token,'Content-Type':'application/json'};
  const get=async path=>{const response=await fetch('/api'+path,{headers});if(!response.ok)throw Error('Synthetic read failed '+response.status);return response.json();};
  const prices=await get('/price-updates/admin/history'),audits=await get('/audit-logs'),payments=await get('/payments');
  const body='x'.repeat(4*1024*1024+1);
  const denied=await fetch('/api/payments/webhook',{method:'POST',headers:{'Content-Type':'application/json'},body});
  const rejection={status:denied.status,body:await denied.json()};
  const preserved=JSON.stringify(prices)===JSON.stringify(await get('/price-updates/admin/history'))&&JSON.stringify(audits)===JSON.stringify(await get('/audit-logs'))&&JSON.stringify(payments)===JSON.stringify(await get('/payments'));
  // Fabricated bytes stay in memory. Preserve the existing decoded 2MiB limit;
  // this checks compatibility of the encoded data URI with the new HTTP budget.
  const screenshot='data:image/png;base64,'+btoa('\0'.repeat(2*1024*1024));
  const valid=await fetch('/api/feedback',{method:'POST',headers,body:JSON.stringify({rating:5,comment:'Synthetic maximum-size screenshot compatibility',screenshot_data:screenshot})});
  const saved=await valid.json();
  return {rejection,preserved,maximum_screenshot_status:valid.status,maximum_screenshot_unchanged:saved.screenshot_data===screenshot};
 });
 assert.equal(result.rejection.status,413);assert.deepEqual(result.rejection.body,{detail:'Request body is too large'});
 assert.equal(result.preserved,true);assert.equal(result.maximum_screenshot_status,201);assert.equal(result.maximum_screenshot_unchanged,true);
 await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();assert.ok(await page.getByRole('button',{name:'Search prices',exact:true}).count());
 assert.equal(outside,0);
 const report={checks:{oversized_payment_body_rejected_before_provider:true,saved_prices_audits_payments_preserved:true,existing_two_mib_screenshot_accepted_unchanged:true,original_current_prices_screen:true},maximum_single_body_test_bytes:4*1024*1024+1,files_created_for_payloads:0,synthetic_preview_reseed_required:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/request-bounds-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
