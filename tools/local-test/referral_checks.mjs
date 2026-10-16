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
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function loginReferrer(){
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('referrer@example.com');
 await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Referrer'}).waitFor();
}
async function snapshot(){
 return page.evaluate(async()=>{
  const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token'),headers={Authorization:'Bearer '+token};
  const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
  const subscription=await fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
  const referral=await fetch('/api/auth/referral-summary',{headers}).then(r=>r.json());return {user,subscription,referral};
 });
}
try {
 await loginReferrer();const before=await snapshot();
 await page.getByRole('button',{name:'Log out',exact:true}).click();await page.waitForURL(origin+'/');
 await page.goto(origin+'/register?ref='+before.referral.referral_code);
 await page.getByRole('heading',{name:'Create your PriceYard account',exact:true}).waitFor();
 assert.ok((await page.locator('body').innerText()).includes(before.referral.referral_code));
 const email='synthetic-referral-'+crypto.randomUUID()+'@example.com';
 await page.getByLabel('Full name',{exact:true}).fill('Synthetic browser referral');await page.getByLabel('Email',{exact:true}).fill(email);
 await page.getByLabel(/Password/).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Register',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Synthetic browser referral'}).waitFor();
 const child=await snapshot();assert.equal(child.subscription.status,'trial');
 assert.equal(new Date(child.subscription.trial_ends_at)-new Date(child.subscription.trial_started_at),14*86400000);
 await page.getByRole('button',{name:'Log out',exact:true}).click();await page.waitForURL(origin+'/');
 await loginReferrer();const after=await snapshot();
 assert.equal(new Date(after.subscription.trial_ends_at)-new Date(before.subscription.trial_ends_at),7*86400000);
 assert.equal(after.referral.referred_count,before.referral.referred_count+1);assert.equal(after.referral.reward_days,7);
 await page.getByRole('heading',{name:'Get 7 extra trial days per referral',exact:true}).waitFor();
 assert.equal(outside,0);
 const report={original_registration_and_referral_link:true,new_account_trial_days:14,referrer_added_days:7,referred_count_increased_once:true,original_dashboard_wording:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/referral-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
