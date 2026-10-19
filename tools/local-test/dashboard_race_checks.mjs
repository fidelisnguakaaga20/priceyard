import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const expectBug=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const checks={},errors=[];let outside=0;
function deferred(){let resolve;const promise=new Promise(done=>{resolve=done;});return {promise,resolve};}
async function settle(page){await page.evaluate(()=>new Promise(done=>requestAnimationFrame(()=>requestAnimationFrame(done))));}
async function login(page,email='free@example.com'){
  const session=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/browser/session'&&r.request().method()==='GET');
  await page.goto(origin+'/login');
  if((await session).ok()){
    const logout=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/logout'&&r.request().method()==='POST');
    await page.getByRole('button',{name:'Log out',exact:true}).click();await logout;await page.goto(origin+'/login');
  }
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test '+(email.startsWith('free')?'Free':'Paid'),exact:true}).waitFor();
}
async function setup(){
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
  await context.addInitScript(()=>{
    localStorage.setItem('priceyard_onboarding_seen','1');window.__checkoutCompleted=0;window.__dashboardReadAborted=0;
    const native=window.fetch.bind(window);
    window.fetch=async(input,options={})=>{
      const url=new URL(typeof input==='string'?input:input.url,location.href);
      if(['/api/auth/referral-summary','/api/price-updates/my-stats'].includes(url.pathname)&&options.signal){
        options.signal.addEventListener('abort',()=>window.__dashboardReadAborted++,{once:true});
      }
      if(url.pathname!=='/api/payments/initiate')return native(input,options);
      // Simulate a transport that finishes despite cancellation. The component
      // must independently reject replies from a disposed account/page.
      const {signal,...remaining}=options;
      try{const response=await native(input,remaining);await response.clone().arrayBuffer();return response;}
      finally{window.__checkoutCompleted++;}
    };
  });
  const page=await context.newPage();page.setDefaultTimeout(12000);page.on('pageerror',e=>errors.push(e.message));
  await login(page);return {page,context};
}
const monthly=page=>page.getByRole('button',{name:/2,500/});
try{
  for(const result of ['success','failure']){
    const {page,context}=await setup(),held=deferred(),release=deferred();
    try{
      await page.route(origin+'/api/payments/initiate',async route=>{
        held.resolve();await release.promise;
        await route.fulfill(result==='success'?{json:{authorization_url:origin+'/faq?synthetic_checkout=1',reference:'fabricated-only'}}:{status:503,json:{detail:'Synthetic delayed checkout failure'}});
      });
      await monthly(page).click();await held.promise;
      await page.locator('a[href="/prices"]').first().click();await page.waitForURL('**/prices');
      release.resolve();
      await page.waitForFunction(()=>window.__checkoutCompleted===1||location.search==='?synthetic_checkout=1');await settle(page);
      checks[result==='success'?'late_checkout_cannot_redirect_departed_page':'late_checkout_cannot_toast_departed_page']=result==='success'?new URL(page.url()).pathname==='/prices':await page.locator('.toast-message').filter({hasText:'Synthetic delayed checkout failure'}).count()===0;
    }finally{release.resolve();await context.close();}
  }
  if(!expectBug){
    const {page,context}=await setup(),held=deferred(),release=deferred();
    try{
      await page.route(origin+'/api/payments/initiate',async route=>{
        held.resolve();await release.promise;await route.fulfill({status:503,json:{detail:'Synthetic previous-account checkout failure'}});
      });
      await monthly(page).click();await held.promise;
      const other=await context.newPage();other.setDefaultTimeout(12000);await login(other,'paid@example.com');
      await page.evaluate(()=>dispatchEvent(new Event('focus')));
      await page.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();
      release.resolve();await page.waitForFunction(()=>window.__checkoutCompleted===1);await settle(page);
      checks.old_account_checkout_cannot_show_new_account_error=await page.locator('.toast-message').filter({hasText:'Synthetic previous-account checkout failure'}).count()===0;
      checks.paid_account_keeps_existing_access=await monthly(page).count()===0;
    }finally{release.resolve();await context.close();}
  }
  if(!expectBug){
    const {page,context}=await setup(),held=deferred(),release=deferred();
    try{
      await page.route(origin+'/api/auth/referral-summary',async route=>{
        held.resolve();await release.promise;
        await route.fulfill({json:{referral_code:'fabricated-obsolete-code',referred_count:0,reward_days:7}}).catch(()=>{});
      });
      await page.reload();await held.promise;
      await page.getByRole('heading',{name:'Welcome, Test Free',exact:true}).waitFor();
      await page.locator('a[href="/prices"]').first().click();await page.waitForURL('**/prices');
      await page.waitForFunction(()=>window.__dashboardReadAborted>0);
      release.resolve();checks.disposed_dashboard_cancels_private_reads=true;
    }finally{release.resolve();await context.close();}
  }
  {
    const {page,context}=await setup();let requests=0;
    try{
      assert.equal(await page.getByRole('button',{name:/6,000/}).count(),1);
      await page.route(origin+'/api/payments/initiate',route=>{
        requests++;return route.fulfill(requests===1?{status:503,json:{detail:'Synthetic retryable checkout failure'}}:{json:{authorization_url:origin+'/faq?synthetic_checkout=1',reference:'fabricated-only'}});
      });
      await monthly(page).click();await page.locator('.toast-message').filter({hasText:'Synthetic retryable checkout failure'}).waitFor();
      await monthly(page).waitFor({state:'visible'});assert.equal(await monthly(page).isEnabled(),true);
      await monthly(page).click();await page.waitForURL('**/faq?synthetic_checkout=1');
      checks.current_checkout_failure_can_retry=true;checks.current_checkout_success_redirects=true;checks.existing_plan_buttons_preserved=true;
      assert.equal(requests,2);
    }finally{await context.close();}
  }
  assert.equal(outside,0);assert.deepEqual(errors,[]);
  const failures=Object.entries(checks).filter(([,ok])=>!ok).map(([name])=>name);
  const report={checks,failures,expected_original_bug:expectBug,production_connections:0,real_payment_requests:0,external_browser_requests:outside,page_errors:errors};
  fs.writeFileSync(path.join(lab,'runtime/dashboard-race-'+(expectBug?'before':'after')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(expectBug)assert.equal(failures.length,2,'Both original late-checkout bugs must reproduce');else assert.deepEqual(failures,[]);
}finally{await browser.close();}
