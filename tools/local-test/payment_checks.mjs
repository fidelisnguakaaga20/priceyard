import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();
page.setDefaultTimeout(12000);
try {
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill('payment@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test Payment'}).waitFor();
  async function snapshot() {
    return page.evaluate(async()=>{
      const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
      const headers={Authorization:'Bearer '+token};
      const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
      const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
      const history=(await fetch('/api/price-updates/history',{headers})).status;
      const initiate=(await fetch('/api/payments/initiate',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({plan:'monthly'})})).status;
      return {subscription:subscription.status,end:subscription.end_date,history,live_initiation:initiate};
    });
  }
  const before=await snapshot();
  assert.deepEqual(before,{subscription:'free',end:null,history:403,live_initiation:503});
  const controls=await context.newPage();
  await controls.goto(origin+'/__test__/payments');
  async function send(name) {
    const response=controls.waitForResponse(r=>r.url()===origin+'/__test__/payment-event'&&r.request().method()==='POST');
    await controls.getByRole('button',{name,exact:true}).click();
    return (await response).json();
  }
  const wrong=await send('Send wrong-amount test event');
  assert.equal(wrong.webhook_status,422);
  assert.equal(wrong.payment_status,'pending');
  assert.equal(wrong.subscription_status,'free');
  await page.reload();
  await page.getByRole('heading',{name:'Welcome, Test Payment'}).waitFor();
  assert.deepEqual(await snapshot(),before);
  const failure=await send('Simulate activation failure');
  assert.equal(failure.webhook_status,500);
  assert.equal(failure.payment_status,'pending');
  assert.equal(failure.subscription_status,'free');
  await page.reload();
  await page.getByRole('heading',{name:'Welcome, Test Payment'}).waitFor();
  assert.deepEqual(await snapshot(),before);
  const valid=await send('Send valid test event');
  assert.equal(valid.webhook_status,200);
  assert.equal(valid.payment_status,'success');
  assert.equal(valid.subscription_status,'active');
  await page.reload();
  await page.getByRole('heading',{name:'Welcome, Test Payment'}).waitFor();
  const after=await snapshot();
  assert.equal(after.subscription,'active');
  assert.equal(after.history,200);
  assert.equal(after.live_initiation,503);
  assert.ok((await page.locator('body').innerText()).includes('Active Paid'));
  assert.deepEqual(await send('Send valid test event'),valid);
  const report={before,wrong_amount_rejected:true,activation_failure_keeps_pending_and_retry_recovers:true,valid_synthetic_event_credited:true,repeat_keeps_same_expiry:true,after,original_dashboard_verified:true,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/payment-checks.json'),JSON.stringify(report,null,2));
  await page.screenshot({path:path.join(lab,'runtime/payment-after.png'),fullPage:true});
  console.log(JSON.stringify(report));
} finally {await browser.close();}
