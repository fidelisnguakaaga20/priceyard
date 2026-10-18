import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug'),results=[];
let external=0;
try {
  for(const scenario of ['normal','native_failure','late_lookup']) {
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();external++;return route.abort();});
    await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
    const page=await context.newPage();page.setDefaultTimeout(12000);
    async function login(name) {
      await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(name+'@example.com');
      await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
      await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
    }
    await login('free');
    const fixture=await page.evaluate(async scenario=>{
      const session=await fetch('/api/auth/browser/session').then(r=>r.json());const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};
      const key=await crypto.subtle.generateKey({name:'ECDH',namedCurve:'P-256'},true,['deriveBits']);
      const encode=value=>btoa(String.fromCharCode(...new Uint8Array(value))).replace(/\+/g,'-').replace(/\//g,'_').replace(/=+$/,'');
      const keys={p256dh:encode(await crypto.subtle.exportKey('raw',key.publicKey)),auth:encode(crypto.getRandomValues(new Uint8Array(16)))};
      const current='https://fcm.googleapis.com/fcm/send/synthetic-logout-'+crypto.randomUUID(),other=current+'-other-device';
      for(const endpoint of [current,other]) {
        const response=await fetch('/api/push/subscribe',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({endpoint,keys})});
        if(response.status!==204)throw Error('Synthetic subscription storage failed');
      }
      window.__nativeLogoutCalls=0;
      const subscription={endpoint:current,unsubscribe:async()=>{window.__nativeLogoutCalls++;if(scenario==='native_failure')throw Error('Synthetic native unsubscribe failure');return true;}};
      const registration={pushManager:{getSubscription:async()=>subscription}};
      Object.defineProperty(navigator.serviceWorker,'getRegistration',{configurable:true,value:()=>scenario==='late_lookup'?new Promise(resolve=>window.__releaseLogoutLookup=()=>resolve(registration)):Promise.resolve(registration)});
      return {current,other};
    },scenario);
    fixture.oldToken=(await context.cookies()).find(cookie=>cookie.name==='priceyard_local_session').value;
    const revoked=page.waitForResponse(r=>r.url()===origin+'/api/auth/logout'&&r.request().method()==='POST');
    await page.getByRole('button',{name:'Log out',exact:true}).click();
    assert.equal((await revoked).status(),204);
    assert.equal(await page.evaluate(()=>localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token')),null);
    const oldStatus=await page.evaluate(async token=>(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status,fixture.oldToken);
    assert.equal(oldStatus,401);
    // Keep one document alive when replacing the account, so an old native
    // lookup really can resolve after the new login, rather than being discarded
    // by a full browser document navigation.
    await page.waitForURL(origin+'/');await page.getByRole('link',{name:'Log in',exact:true}).first().click();
    await page.getByLabel('Email',{exact:true}).fill('free@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:'Welcome, Test Free'}).waitFor();
    if(scenario==='late_lookup')await page.evaluate(()=>window.__releaseLogoutLookup?.());
    await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,100)));
    const saved=await page.evaluate(async fixture=>{
      const session=await fetch('/api/auth/browser/session').then(r=>r.json());const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};

      async function owned(endpoint){return (await fetch('/api/push/subscribed?endpoint='+encodeURIComponent(endpoint),{headers}).then(r=>r.json())).subscribed;}
      return {current:await owned(fixture.current),other:await owned(fixture.other),native_calls:window.__nativeLogoutCalls||0,me:(await fetch('/api/auth/me',{headers})).status};
    },fixture);
    assert.equal(saved.other,true);assert.equal(saved.me,200);
    if(scenario==='late_lookup') {assert.equal(saved.current,true);assert.equal(saved.native_calls,0);}
    else {assert.equal(saved.current,expectBug);assert.equal(saved.native_calls,expectBug?0:1);}
    results.push({scenario,old_token_status:oldStatus,current_device_retained:saved.current,other_device_preserved:saved.other,native_calls:saved.native_calls,new_session_status:saved.me});
    // Remove only the fabricated subscriptions created by this scenario.
    await page.evaluate(async fixture=>{
      const session=await fetch('/api/auth/browser/session').then(r=>r.json());const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};
      for(const endpoint of [fixture.current,fixture.other])await fetch('/api/push/unsubscribe',{method:'POST',headers:{...headers,'Content-Type':'application/json'},body:JSON.stringify({endpoint})});
    },fixture);
    await context.close();
  }
  assert.equal(external,0);
  const report={checks:results,expected_original_bug:expectBug,native_calls_are_local_mocks:true,real_notifications:0,external_page_requests:external,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/logout-push-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
