import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let outside=0;
async function fixture(email) {
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');
 await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();return {context,page};
}
try {
 const customer=await fixture('manual-paid');
 async function snapshot() {
  return customer.page.evaluate(async()=>{
   const session=await fetch('/api/auth/browser/session').then(r=>r.json());
   const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};
   const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
   const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
   const history=(await fetch('/api/price-updates/history',{headers})).status;
   const checkout=(await fetch('/api/payments/initiate',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({plan:'monthly'})})).status;
   return {id:user.id,status:subscription.status,end:subscription.end_date,history,checkout};
  });
 }
 const before=await snapshot();assert.equal(before.status,'active');assert.equal(before.end,null);assert.equal(before.history,200);assert.equal(before.checkout,409);
 const controls=await customer.context.newPage();await controls.goto(origin+'/__test__/manual-review');
 async function send(){const response=controls.waitForResponse(r=>r.url()===origin+'/__test__/payment-event'&&r.request().method()==='POST');await controls.getByRole('button',{name:'Send fake purchase for review',exact:true}).click();return (await response).json();}
 const held=await send();assert.equal(held.webhook_status,409);assert.equal(held.payment_status,'pending');assert.equal(held.end_date,null);
 assert.deepEqual(await send(),held);assert.deepEqual(await snapshot(),before);
 const admin=await fixture('admin');
 async function audits(){return admin.page.evaluate(async()=>{
  const rows=await fetch('/api/audit-logs').then(r=>r.json());
  return rows.filter(row=>row.action==='payment.review_required');
 });}
 const review=await audits();assert.equal(review.length,1);assert.equal(review[0].new_value.paystack_transaction_id,'700005');
 await admin.page.goto(origin+'/admin/subscriptions');await admin.page.getByRole('heading',{name:'Subscriptions',exact:true}).waitFor();
 const row=admin.page.getByRole('cell',{name:'#'+before.id,exact:true}).locator('..');
 const resolved=admin.page.waitForResponse(r=>r.url()===origin+'/api/subscriptions/'+before.id+'/status'&&r.request().method()==='PATCH');
 await row.getByRole('combobox').selectOption('free');assert.equal((await resolved).status(),200);
 const credited=await send();assert.equal(credited.webhook_status,200);assert.equal(credited.payment_status,'success');
 assert.deepEqual(await send(),credited);
 await customer.page.reload();await customer.page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
 const after=await snapshot();assert.equal(after.status,'active');assert.ok(after.end);assert.equal(after.history,200);assert.equal(after.checkout,503);
 assert.equal((await audits()).length,1);assert.equal(outside,0);
 const report={indefinite_checkout_blocked:true,confirmed_purchase_held_without_expiring_grant:true,receipt_preserved_once:true,original_admin_subscription_control_resolves_test_grant:true,purchase_then_credits_once:true,after,external_page_requests:outside,live_provider_connections:0,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/manual-review-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
