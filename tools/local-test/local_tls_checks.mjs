import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='https://127.0.0.1:55446';
const identity=JSON.parse(fs.readFileSync(path.join(lab,'runtime/local-tls-20261018/public-identity.json'),'utf8'));
assert.equal(identity.purpose,'synthetic-loopback-only-no-system-trust-change');assert.equal(identity.origin,origin);
assert.match(identity.spki_sha256,/^[A-Za-z0-9+/]{43}=$/);
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
// Trust this one generated SPKI in this disposable browser only. No broad
// ignoreHTTPSErrors flag, OS certificate installation or external navigation.
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update',
  '--disable-sync','--no-first-run','--ignore-certificate-errors-spki-list='+identity.spki_sha256]});
const context=await browser.newContext({serviceWorkers:'block'});let outside=0;
await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
try{
 const response=await page.goto(origin+'/login');assert.equal(response.status(),200);
 const security=await response.securityDetails();assert.match(security.protocol,/TLS ?1\.[23]/);
 assert.deepEqual(await page.evaluate(()=>fetch('/__test__/tls').then(r=>r.json())),{synthetic_only:true,providers:'disabled',tls_fixture:true});
 await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await page.getByLabel('Remember me',{exact:true}).setChecked(false);
 await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const cookie=(await context.cookies()).find(c=>c.name==='__Host-priceyard_session');
 assert.ok(cookie);assert.equal(cookie.secure,true);assert.equal(cookie.httpOnly,true);assert.equal(cookie.sameSite,'Lax');assert.equal(cookie.path,'/');assert.equal(cookie.expires,-1);
 assert.deepEqual(await page.evaluate(()=>({local:localStorage.getItem('priceyard_access_token'),session:sessionStorage.getItem('priceyard_access_token'),cookie:document.cookie.includes('priceyard_session')})),{local:null,session:null,cookie:false});
 const guarded=await page.evaluate(async()=>({profile:(await fetch('/api/auth/me')).status,
   csrf:(await fetch('/api/auth/logout',{method:'POST'})).status,
   cache:(await fetch('/api/auth/browser/session')).headers.get('cache-control')}));
 assert.equal(guarded.profile,200);assert.equal(guarded.csrf,403);assert.equal(guarded.cache,'private, no-store');
 await page.reload();await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
 const logout=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/logout'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Log out',exact:true}).click();assert.equal((await logout).status(),204);
 assert.equal((await context.cookies()).some(c=>c.name==='__Host-priceyard_session'),false);
 const revoked=await page.evaluate(async token=>(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status,cookie.value);assert.equal(revoked,401);
 assert.equal(outside,0);
 const result={passed:true,tls_protocol:security.protocol,actual_loopback_tls_handshake:true,
  secure_host_http_only_cookie:true,unremembered_session_cookie:true,original_login_reload_logout:true,
  csrf_rejected:true,server_revocation_verified:true,javascript_login_secret_absent:true,
  process_local_spki_pin_only:true,system_trust_store_changed:false,
  real_host_certificate_proxy_dns_verified:false,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'evidence/batch-86-tls-browser.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result));
}finally{await browser.close();}
