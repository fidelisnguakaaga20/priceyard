import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const expectBug=process.argv.includes('--expect-bug');
const result={};
async function makePage(){
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  await context.addInitScript(()=>{
    localStorage.setItem('priceyard_onboarding_seen','1');
    const original=window.fetch.bind(window);let sequence=0;
    window.fetch=(input,options={})=>{
      if(new URL(typeof input==='string'?input:input.url,location.href).pathname==='/api/auth/me'){
        const headers=new Headers(options.headers);headers.set('X-Local-Test-Sequence',String(++sequence));
        return original(input,{...options,headers});
      }
      return original(input,options);
    };
  });
  const page=await context.newPage();page.setDefaultTimeout(12000);
  return {context,page};
}
async function login(page,email='trial@example.com',navigate=true){
  if(navigate)await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
}
try{
  {
    const {context,page}=await makePage();
    let count=0,held;
    await page.route('**/api/auth/me',route=>{if(route.request().headers()['x-local-test-sequence']==='1'){held=route;return;}return route.continue()});
    await login(page);
    assert.ok(held,'First profile request must be pending');
    const profile=await page.evaluate(async()=>{
      const token=localStorage.getItem('priceyard_access_token');
      return fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}}).then(r=>r.json());
    });
    await page.getByRole('button',{name:'Log out',exact:true}).click();
    const released=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/me');
    await held.fulfill({status:200,contentType:'application/json',body:JSON.stringify(profile)});
    await released;
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    if(expectBug)await page.getByRole('button',{name:'Log out',exact:true}).waitFor();
    else await page.getByRole('button',{name:'Log out',exact:true}).waitFor({state:'hidden'});
    const restored=await page.getByRole('button',{name:'Log out',exact:true}).isVisible();
    assert.equal(restored,expectBug);
    assert.equal(await page.evaluate(()=>localStorage.getItem('priceyard_access_token')),null);
    result.delayed_profile_after_logout={reproduced:expectBug,logout_stays_visible_as_guest:!restored};
    await context.close();
  }
  {
    const {context,page}=await makePage();
    await login(page);
    await page.route('**/api/auth/me',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic account outage'})}));
    await page.reload();
    await page.getByRole('heading',{name:'Log in to PriceYard',exact:true}).waitFor();
    const retained=await page.evaluate(()=>Boolean(localStorage.getItem('priceyard_access_token')));
    assert.equal(retained,!expectBug);
    if(!expectBug){
      await page.unroute('**/api/auth/me');
      await page.reload();
      await page.waitForURL('**/dashboard');
      await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
    }
    result.temporary_account_outage={stored_session_preserved:retained,recovers_without_new_password:!expectBug};
    await context.close();
  }
  if(!expectBug){
    const {context,page}=await makePage();
    let count=0,held;
    await page.route('**/api/auth/me',route=>{if(route.request().headers()['x-local-test-sequence']==='1'){held=route;return;}return route.continue()});
    await login(page);
    await page.getByRole('button',{name:'Log out',exact:true}).click();
    // Layout's existing logout handler finishes on the homepage. A transient
    // protected-route redirect to Login is not a stable navigation contract.
    await page.waitForURL(origin+'/');
    await page.getByRole('link',{name:'Log in',exact:true}).click();
    await login(page,'admin@example.com',false);
    await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
    const released=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/me'&&response.status()===401);
    await held.fulfill({status:401,contentType:'application/json',body:JSON.stringify({detail:'Synthetic old-session rejection'})});
    await released;
    await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
    await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
    assert.ok(await page.evaluate(()=>Boolean(localStorage.getItem('priceyard_access_token'))));
    result.old_token_rejection_after_account_switch={new_account_remains_signed_in:true};
    await context.close();
  }
  const report={expected_original_defects:expectBug,result,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/account-'+(expectBug?'before':'after')+'.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{await browser.close()}
