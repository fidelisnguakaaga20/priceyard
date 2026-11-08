import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0,raw;await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url,method='GET',body,token) {
  return page.evaluate(async({url,method,body,token})=>{const response=await fetch('/api'+url,{method,headers:{'Content-Type':'application/json',...(token?{Authorization:'Bearer '+token}:{})},...(body?{body:JSON.stringify(body)}:{})});return {status:response.status,body:response.status===204?null:await response.json()};},{url,method,body,token});
}
async function resetLink() {
  assert.equal((await api('/auth/forgot-password','POST',{email:'reset@example.com'})).status,200);
  return page.evaluate(async()=>{const html=await fetch('/__test__/inbox').then(response=>response.text());const doc=new DOMParser().parseFromString(html,'text/html');const links=[...doc.querySelectorAll('a')].filter(node=>node.textContent==='Open reset link for reset@example.com');return links.at(-1)?.getAttribute('href');});
}
try {
  await page.goto(origin+'/login');
  const initial=await api('/auth/login','POST',{email:'reset@example.com',password:'PriceYardDemo8!'});assert.equal(initial.status,200);
  const oldToken=initial.body.access_token,profile=await api('/auth/me','GET',undefined,oldToken);
  const before=(await api('/subscriptions/'+profile.body.id,'GET',undefined,oldToken)).body;
  const link=await resetLink();assert.ok(link?.startsWith(origin+'/reset-password?'));raw=new URL(link).searchParams.get('token');await page.goto(link);
  const password=page.locator('#reset-password'),confirmation=page.locator('#confirm-reset-password');
  let submitted=0;page.on('request',request=>{if(request.url()===origin+'/api/auth/reset-password'&&request.method()==='POST')submitted++;});
  await password.fill('好'.repeat(25));await confirmation.fill('好'.repeat(25));await page.getByRole('button',{name:'Reset password',exact:true}).click();assert.equal(submitted,0);assert.equal(await password.evaluate(node=>node.validationMessage),'Password is too long');
  assert.equal((await api('/auth/reset-password','POST',{token:raw,new_password:'好'.repeat(25)})).status,422);
  assert.equal((await api('/auth/me','GET',undefined,oldToken)).status,200);
  await password.fill('好'.repeat(24));await confirmation.fill('好'.repeat(24));
  const saved=page.waitForResponse(response=>response.url()===origin+'/api/auth/reset-password'&&response.request().method()==='POST');await page.getByRole('button',{name:'Reset password',exact:true}).click();assert.equal((await saved).status(),200);
  await page.getByRole('heading',{name:'Password updated',exact:true}).waitFor();assert.equal((await api('/auth/me','GET',undefined,oldToken)).status,401);
  assert.equal((await api('/auth/reset-password','POST',{token:raw,new_password:'AnotherSynthetic8!'})).status,400);
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('reset@example.com');await page.getByLabel('Password',{exact:true}).fill('好'.repeat(24));await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Reset',exact:true}).waitFor();
  const after=await page.evaluate(async id=>fetch('/api/subscriptions/'+id,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}}).then(response=>response.json()),profile.body.id);assert.deepEqual(after,before);assert.equal(outside,0);
  // Keep the real reset-request cooldown. Reseed only the disposable preview
  // after this check instead of requesting another link immediately to clean up.
  const report={native_forms_reject_before_post:true,direct_overlong_request_is_422:true,rejected_attempt_preserves_link_and_old_login:true,same_link_accepts_exact_utf8_boundary:true,previous_token_revoked_after_success:true,link_remains_single_use:true,original_login_form_accepts_unicode_password:true,subscription_value_unchanged:true,synthetic_fixture_reseed_required:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/password-reset-boundary-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {
  await browser.close();
}
