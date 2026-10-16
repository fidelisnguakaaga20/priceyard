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
let fulfilledCheckout=0,blockedExternal=0;
await context.route('**/*',route=>{
  const url=route.request().url();
  if(new URL(url).origin===origin)return route.continue();
  if(url==='https://checkout.paystack.com/priceyard-synthetic-only') {
    fulfilledCheckout++;return route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><title>Fabricated checkout</title><h1>Local synthetic checkout interception</h1><p>No provider connection was made.</p>'});
  }
  blockedExternal++;return route.abort();
});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
const controls=await context.newPage();
async function mode(value) {
  return controls.evaluate(async mode=>{
    const response=await fetch('/__test__/checkout-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})});
    if(!response.ok)throw Error('Fixture mode failed');return response.json();
  },value);
}
try {
  await controls.goto(origin+'/__test__/checkout');await mode('disabled');
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill('free@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test Free'}).waitFor();
  async function state(initiate=false) {
    return controls.evaluate(async initiate=>{
      const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
      const headers={Authorization:'Bearer '+token};
      const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
      const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
      const history=(await fetch('/api/price-updates/history',{headers})).status;
      const initiation=initiate?(await fetch('/api/payments/initiate',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({plan:'monthly'})})).status:null;
      return {status:subscription.status,history,initiation};
    },initiate);
  }
  assert.deepEqual(await state(true),{status:'free',history:403,initiation:503});
  await controls.getByRole('button',{name:'Use fake unsafe checkout reply',exact:true}).click();
  await controls.locator('#result').filter({hasText:'unsafe_link'}).waitFor();
  const rejected=[];
  for(const label of ['₦2,500 / month','₦6,000 / 3 months']) {
    const response=page.waitForResponse(r=>r.url()===origin+'/api/payments/initiate'&&r.request().method()==='POST');
    await page.getByRole('button',{name:label,exact:true}).click();
    const reply=await response;assert.equal(reply.status(),502);
    await page.getByText('Payment provider did not return a checkout link',{exact:true}).first().waitFor();
    assert.equal(page.url(),origin+'/dashboard');
    assert.deepEqual(await state(),{status:'free',history:403,initiation:null});
    rejected.push({plan:JSON.parse(reply.request().postData()).plan,status:reply.status(),dashboard_retained:true});
  }
  await mode('valid');
  const response=page.waitForResponse(r=>r.url()===origin+'/api/payments/initiate'&&r.request().method()==='POST');
  await page.getByRole('button',{name:'₦2,500 / month',exact:true}).click();
  assert.equal((await response).status(),200);
  await page.waitForURL('https://checkout.paystack.com/priceyard-synthetic-only');
  await page.getByRole('heading',{name:'Local synthetic checkout interception'}).waitFor();
  assert.deepEqual(await state(),{status:'free',history:403,initiation:null});
  await controls.getByRole('button',{name:'Disable checkout fixture',exact:true}).click();
  await controls.locator('#result').filter({hasText:'disabled'}).waitFor();
  assert.deepEqual(await state(true),{status:'free',history:403,initiation:503});
  assert.equal(fulfilledCheckout,1);assert.equal(blockedExternal,0);
  const report={rejected,valid_original_button_navigation_mocked:true,checkout_never_grants_access:true,fixture_disabled_afterward:true,checkout_navigation_fulfilled_locally:fulfilledCheckout,unexpected_external_requests:blockedExternal,live_provider_connections:0,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/checkout-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {
  try {await mode('disabled');} finally {await browser.close();}
}
