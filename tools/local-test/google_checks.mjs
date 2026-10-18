import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',checks={};let outside=0,control;
async function page(){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const result=await context.newPage();result.setDefaultTimeout(15000);await result.goto(origin+'/login');return result;
}
async function mode(value){assert.equal(await control.evaluate(async mode=>(await fetch('/__test__/google-mode',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})})).status,value),200);}
async function googleLogin(p){return p.evaluate(async()=>{
 const response=await fetch('/api/auth/browser/google',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id_token:'synthetic-preview-google-token'})});
 const data=await response.json();
 return {status:response.status,detail:data.detail};
});}
async function account(p){return p.evaluate(async()=>{
 const session=await fetch('/api/auth/browser/session').then(r=>r.json());
 const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};
 const userResponse=await fetch('/api/auth/me',{headers});if(!userResponse.ok)throw Error('Local account read failed');
 const user=await userResponse.json(),subscriptionResponse=await fetch('/api/subscriptions/'+user.id,{headers});
 if(!subscriptionResponse.ok)throw Error('Local subscription read failed');
 return {user,subscription:await subscriptionResponse.json(),history:(await fetch('/api/price-updates/history',{headers})).status};
});}
try{
 control=await page();
 const existing=await page();await mode('existing_email');const denied=await googleLogin(existing);
 assert.equal(denied.status,409);assert.match(denied.detail,/existing PriceYard email and password/);assert.match(denied.detail,/reset your password/);
 await existing.getByLabel('Email',{exact:true}).fill('trial@example.com');await existing.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await existing.getByRole('button',{name:'Log in',exact:true}).click();await existing.waitForURL('**/dashboard');
 await existing.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();
 const kept=await account(existing);assert.equal(kept.user.email,'trial@example.com');assert.equal(kept.history,200);
 assert.equal(new Date(kept.subscription.trial_ends_at)-new Date(kept.subscription.trial_started_at),14*86400000);
 checks.same_email_cannot_attach_and_original_password_login_works=true;
 for(const [value,heading,email] of [['linked','Welcome, Test Google','google@example.com'],['new','Welcome, Test Google New','new-google@example.com']]){
  const p=await page();await mode(value);assert.equal((await googleLogin(p)).status,200);
  await p.goto(origin+'/dashboard');await p.getByRole('heading',{name:heading,exact:true}).waitFor();
  const state=await account(p);assert.equal(state.user.email,email);assert.equal(state.history,200);
  assert.equal(new Date(state.subscription.trial_ends_at)-new Date(state.subscription.trial_started_at),14*86400000);
  assert.ok((await p.locator('body').innerText()).includes('2,500'));assert.ok((await p.locator('body').innerText()).includes('6,000'));
  checks[value==='linked'?'already_linked_user_keeps_trial_and_history':'new_google_user_gets_original_trial_and_plans']=true;
 }
 for(const [value,status] of [['unverified',401],['outage',503]]){
  const p=await page();await mode(value);const result=await googleLogin(p);assert.equal(result.status,status);
  assert.equal(await p.evaluate(()=>localStorage.getItem('priceyard_access_token')),null);
  if(value==='outage')assert.ok(!result.detail.includes('Fabricated'));
  checks[value+'_does_not_log_in']=true;
 }
 await mode('disabled');assert.equal((await googleLogin(await page())).status,503);checks.live_google_disabled=true;
 assert.equal(outside,0);
 const report={checks,external_page_requests:outside,production_connections:0,verified_claims:'fabricated only; actual cryptographic verifier covered by backend tests',live_google_popup_tested:false};
 fs.writeFileSync(path.join(lab,'runtime/google-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{if(control)await mode('disabled').catch(()=>{});await browser.close();}
