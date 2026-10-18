import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const results=[];
let external=0;
try {
  for (const scenario of [
    {name:'value-paid',before:'active',days:30,button:'Confirm fake monthly renewal'},
    {name:'value-trial',before:'trial',days:90,button:'Confirm fake seasonal trial purchase'}
  ]) {
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>{
      if(new URL(route.request().url()).origin===origin)return route.continue();
      external++;return route.abort();
    });
    await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
    const page=await context.newPage();page.setDefaultTimeout(12000);
    await page.goto(origin+'/login');
    await page.getByLabel('Email',{exact:true}).fill(scenario.name+'@example.com');
    await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();
    await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
    async function snapshot() {
      return page.evaluate(async()=>{
        const session=await fetch('/api/auth/browser/session').then(r=>r.json());
        const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};
        const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
        const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
        const history=(await fetch('/api/price-updates/history',{headers})).status;
        const initiation=(await fetch('/api/payments/initiate',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({plan:'monthly'})})).status;
        return {subscription,history,initiation};
      });
    }
    const before=await snapshot();
    assert.equal(before.subscription.status,scenario.before);
    const anchor=scenario.before==='active'?before.subscription.end_date:before.subscription.trial_ends_at.slice(0,10);
    const expected=new Date(anchor+'T00:00:00Z');expected.setUTCDate(expected.getUTCDate()+scenario.days);
    const expectedEnd=expected.toISOString().slice(0,10);
    const controls=await context.newPage();await controls.goto(origin+'/__test__/purchase-value');
    const displayed=JSON.parse(await controls.locator('#fixtures').innerText());
    assert.equal(displayed[scenario.name].paid_end,before.subscription.end_date);
    assert.ok((displayed[scenario.name].trial_end||'').startsWith(before.subscription.trial_ends_at?.slice(0,10)||''));
    async function send() {
      const response=controls.waitForResponse(r=>r.url()===origin+'/__test__/payment-event'&&r.request().method()==='POST');
      await controls.getByRole('button',{name:scenario.button,exact:true}).click();
      return (await response).json();
    }
    const event=await send();assert.equal(event.webhook_status,200);assert.equal(event.end_date,expectedEnd);
    await page.reload();
    await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
    const after=await snapshot();
    assert.equal(after.subscription.status,'active');assert.equal(after.subscription.end_date,expectedEnd);
    assert.equal(after.subscription.trial_ends_at,before.subscription.trial_ends_at);
    assert.equal(after.history,200);assert.equal(after.initiation,503);
    assert.ok((await page.locator('body').innerText()).includes('Active Paid'));
    assert.deepEqual(await send(),event);
    assert.equal((await snapshot()).subscription.end_date,expectedEnd);
    results.push({account:scenario.name,previous_paid_end:before.subscription.end_date,original_trial_end:before.subscription.trial_ends_at,purchased_days:scenario.days,expected_end:expectedEnd,saved_end:after.subscription.end_date,replay_unchanged:true,original_dashboard:true,live_initiation:after.initiation});
    await page.screenshot({path:path.join(lab,'runtime/'+scenario.name+'-after.png'),fullPage:true});
    await context.close();
  }
  assert.equal(external,0);
  const report={checks:results,external_page_requests:external,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/purchase-value-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {await browser.close();}
