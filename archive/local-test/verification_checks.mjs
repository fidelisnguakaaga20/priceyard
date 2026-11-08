import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug');
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>{
 localStorage.setItem('priceyard_onboarding_seen','1');window.__verificationCompleted=0;
 const original=window.fetch.bind(window);
 window.fetch=async(...args)=>{const response=await original(...args);if(new URL(response.url).pathname.endsWith('/verify'))window.__verificationCompleted++;return response;};
});
const page=await context.newPage();page.setDefaultTimeout(15000);
const controls=await context.newPage();
const callback=origin+'/payment/callback?reference=py_local_verify_only';
async function mode(value) {
 await controls.evaluate(async mode=>{const response=await fetch('/__test__/verification-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})});if(!response.ok)throw Error('Verification fixture failed');},value);
}
async function snapshot() {
 return page.evaluate(async()=>{
  const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
  const headers={Authorization:'Bearer '+token};
  const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
  const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
  const history=(await fetch('/api/price-updates/history',{headers})).status;
  return {status:subscription.status,end:subscription.end_date,history};
 });
}
try {
 await controls.goto(origin+'/__test__/verification');await mode('disabled');
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('verify@example.com');
 await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Verify'}).waitFor();
 assert.deepEqual(await snapshot(),{status:'free',end:null,history:403});
 let report;
 if(expectBug) {
  await mode('valid');await page.goto(callback);await page.getByRole('heading',{name:'Thank you',exact:true}).waitFor();
  await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,300)));
  assert.deepEqual(await snapshot(),{status:'free',end:null,history:403});
  assert.equal(await page.evaluate(()=>window.__verificationCompleted),0);
  assert.ok((await page.title()).startsWith('Payment received'));
  report={expected_original_bug:true,missed_webhook_not_recovered:true,unverified_success_title:true};
 } else {
  await mode('pending');await page.goto(callback);await page.getByRole('heading',{name:'Thank you',exact:true}).waitFor();
  await page.waitForFunction(()=>window.__verificationCompleted===4);
  assert.deepEqual(await snapshot(),{status:'free',end:null,history:403});
  assert.equal(await page.title(),'Payment — PriceYard');
  await page.getByRole('link',{name:'Go to Dashboard',exact:true}).click();
  await page.getByRole('heading',{name:'Welcome, Test Verify'}).waitFor();
  await mode('wrong_amount');
  const rejected=page.waitForResponse(r=>r.url()===origin+'/api/payments/py_local_verify_only/verify');
  await page.goto(callback);assert.equal((await rejected).status(),422);
  assert.deepEqual(await snapshot(),{status:'free',end:null,history:403});
  assert.equal(await page.title(),'Payment — PriceYard');
  await mode('valid');
  await page.getByRole('link',{name:'Go to Dashboard',exact:true}).click();
  await page.getByRole('heading',{name:'Welcome, Test Verify'}).waitFor();
  await page.goto(callback);
  await page.waitForFunction(()=>document.title==='Payment received — PriceYard');
  await page.waitForFunction(()=>document.body.innerText.includes('Active Paid'));
  const confirmed=await snapshot();assert.equal(confirmed.status,'active');assert.equal(confirmed.history,200);
  await page.getByRole('link',{name:'Go to Dashboard',exact:true}).click();
  await page.getByRole('heading',{name:'Welcome, Test Verify'}).waitFor();
  assert.ok((await page.locator('body').innerText()).includes('Active Paid'));
  await page.goto(callback);await page.waitForFunction(()=>document.title==='Payment received — PriceYard');
  assert.deepEqual(await snapshot(),confirmed);
  await page.goto(callback+'&trxref=py_conflicting_reference');
  await page.getByRole('heading',{name:'Thank you',exact:true}).waitFor();
  await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,100)));
  assert.equal(await page.evaluate(()=>window.__verificationCompleted),0);
  assert.equal(await page.title(),'Payment — PriceYard');
  report={pending_bounded_to_four_attempts:true,wrong_amount_not_credited:true,missed_webhook_recovered:true,original_dashboard_refreshes_without_reload:true,replay_expiry_unchanged:true,conflicting_callback_references_not_trusted:true,confirmed,original_callback_markup_preserved:true};
 }
 assert.equal(outside,0);await mode('disabled');
 report={...report,external_page_requests:outside,live_provider_connections:0,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/verification-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {try{await mode('disabled');}finally{await browser.close();}}
