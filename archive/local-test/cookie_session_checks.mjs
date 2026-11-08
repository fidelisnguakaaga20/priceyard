import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
let outside=0;const result={},trace=[];let debugPage,debugContext;
async function makeContext(){const c=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});await c.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});await c.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));return c;}
async function login(page,email,remember=true){await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email);await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByLabel('Remember me',{exact:true}).setChecked(remember);await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test /}).waitFor();}
async function noJsSecret(page){assert.deepEqual(await page.evaluate(()=>({local:localStorage.getItem('priceyard_access_token'),session:sessionStorage.getItem('priceyard_access_token'),cookie:document.cookie.includes('priceyard_local_session')})),{local:null,session:null,cookie:false});}
try{
 const context=await makeContext(),page=await context.newPage();debugContext=context;page.setDefaultTimeout(12000);
 await login(page,'trial@example.com',false);let cookie=(await context.cookies()).find(c=>c.name==='priceyard_local_session');assert.ok(cookie.httpOnly);assert.equal(cookie.expires,-1);await noJsSecret(page);
 const calls=[];page.on('request',r=>{if(new URL(r.url()).pathname.startsWith('/api/'))calls.push(r);});
 const historyResponse=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/price-updates/history');
 await page.goto(origin+'/history');await page.getByRole('heading',{name:'Price history',exact:true}).waitFor();assert.equal((await historyResponse).status(),200);
 assert.ok(calls.some(r=>new URL(r.url()).pathname==='/api/price-updates/history'&&!r.headers().authorization&&r.headers()['x-priceyard-session']));
 const denied=await page.evaluate(async()=> (await fetch('/api/auth/logout',{method:'POST'})).status);assert.equal(denied,403);
 result.http_only_no_js_login_secret_and_csrf=true;
 const second=await context.newPage();debugPage=second;second.on('response',r=>{if(r.url().includes('/api/auth/'))trace.push([new URL(r.url()).pathname,r.status()]);});second.on('requestfailed',r=>trace.push([new URL(r.url()).pathname,'failed']));second.setDefaultTimeout(12000);await second.goto(origin+'/dashboard');await second.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();result.shared_session_reload_and_unremembered_cookie=true;
 const logout=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/logout'&&r.request().method()==='POST');await page.getByRole('button',{name:'Log out',exact:true}).click();assert.equal((await logout).status(),204);
 await second.getByRole('button',{name:'Log out',exact:true}).waitFor({state:'hidden'});assert.equal((await context.cookies()).some(c=>c.name==='priceyard_local_session'),false);
 // Use the approved page transport; the lab deliberately denies Node APIRequest networking.
 const replay=await page.evaluate(async raw=>(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+raw}})).status,cookie.value);assert.equal(replay,401);result.cross_tab_logout_and_server_revocation=true;
 await login(second,'paid@example.com');cookie=(await context.cookies()).find(c=>c.name==='priceyard_local_session');assert.ok(cookie.expires>Date.now()/1000+89*86400&&cookie.expires<=Date.now()/1000+90*86400);await noJsSecret(second);await page.goto(origin+'/dashboard');await page.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();result.remembered_cookie_and_account_switch=true;
 await context.close();
 const offlineContext=await makeContext(),offlinePage=await offlineContext.newPage();offlinePage.setDefaultTimeout(12000);await login(offlinePage,'paid@example.com');
 debugPage=offlinePage;debugContext=offlineContext;
 // Explicitly abort API traffic too: routing can otherwise override browser offline emulation.
 await offlineContext.route('**/api/**',r=>r.abort('internetdisconnected'));
 await offlineContext.setOffline(true);await offlinePage.getByRole('button',{name:'Log out',exact:true}).click();await offlinePage.getByRole('button',{name:'Log out',exact:true}).waitFor({state:'hidden'});
 await offlinePage.waitForFunction(()=>Boolean(localStorage.getItem('priceyard_logout_pending')));await offlineContext.setOffline(false);await offlineContext.unroute('**/api/**');await offlinePage.reload();await offlinePage.getByRole('link',{name:'Log in',exact:true}).first().waitFor();
 await offlinePage.waitForFunction(()=>localStorage.getItem('priceyard_logout_pending')===null);assert.equal((await offlineContext.cookies()).some(c=>c.name==='priceyard_local_session'),false);result.offline_logout_stays_guest_and_retries_revocation=true;
 await offlineContext.close();
 const legacyContext=await makeContext();const legacyPage=await legacyContext.newPage();legacyPage.setDefaultTimeout(12000);await legacyPage.goto(origin+'/__test__/status');
 const credential=await legacyPage.evaluate(async()=>{const r=await fetch('/api/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'trial@example.com',password:'PriceYardDemo8!'})});return(await r.json()).access_token;});
 await legacyPage.evaluate(token=>localStorage.setItem('priceyard_access_token',token),credential);await legacyPage.goto(origin+'/dashboard');await legacyPage.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();await noJsSecret(legacyPage);assert.equal((await legacyContext.cookies()).find(c=>c.name==='priceyard_local_session').value,credential);result.valid_legacy_transport_preserves_signed_token_expiry=true;
 await legacyContext.close();assert.equal(outside,0);
 for(const staleStatus of [200,401]){
  const c=await makeContext(),p=await c.newPage();debugPage=p;debugContext=c;p.setDefaultTimeout(12000);await login(p,'trial@example.com');
  const oldProfile=await p.evaluate(()=>fetch('/api/auth/me').then(r=>r.json()));
  let held,resolveHeld;const pending=new Promise(resolve=>resolveHeld=resolve);
  await p.route('**/api/auth/me',route=>{if(!held){held=route;resolveHeld();return;}return route.continue();});
  await p.evaluate(()=>dispatchEvent(new Event('focus')));await pending;
  const revoked=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/logout');await p.getByRole('button',{name:'Log out',exact:true}).click();assert.equal((await revoked).status(),204);
  await p.waitForURL(origin+'/');await p.getByRole('link',{name:'Log in',exact:true}).first().click();
  await p.getByLabel('Email',{exact:true}).fill('paid@example.com');await p.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await p.getByRole('button',{name:'Log in',exact:true}).click();await p.waitForURL('**/dashboard');await p.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();
  const released=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/me'&&r.status()===staleStatus);
  await held.fulfill({status:staleStatus,contentType:'application/json',body:JSON.stringify(staleStatus===200?oldProfile:{detail:'Synthetic expired old login'})});await released;
  await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));await p.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();await noJsSecret(p);await c.close();
 }
 result.delayed_profile_and_old_401_cannot_replace_new_account=true;
 {
  const c=await makeContext(),p=await c.newPage();p.setDefaultTimeout(12000);await login(p,'trial@example.com');
  let held;await p.route('**/api/auth/logout',route=>{held=route;});
  const request=p.waitForRequest('**/api/auth/logout');await p.getByRole('button',{name:'Log out',exact:true}).click();await request;
  const other=await c.newPage();other.setDefaultTimeout(12000);await other.goto(origin+'/login');await other.getByLabel('Email',{exact:true}).fill('paid@example.com');await other.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  let sent=0;other.on('request',r=>{if(new URL(r.url()).pathname==='/api/auth/browser/login')sent++;});
  await other.getByRole('button',{name:'Log in',exact:true}).click();await other.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert.equal(sent,0);const locks=await other.evaluate(()=>navigator.locks.query());assert.ok(locks.held.some(lock=>lock.name==='priceyard-browser-session'));
  await held.continue();await other.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();assert.equal(sent,1);await other.reload();await other.getByRole('heading',{name:'Welcome, Test Paid',exact:true}).waitFor();await c.close();
 }
 result.delayed_logout_response_cannot_clear_new_cross_tab_signin=true;
 {
  const c=await makeContext(),p=await c.newPage();p.setDefaultTimeout(12000);await login(p,'trial@example.com');
  let held;await p.route('**/api/auth/browser/session',route=>{held=route;});
  const pending=p.waitForRequest('**/api/auth/browser/session');await p.evaluate(()=>dispatchEvent(new Event('focus')));await pending;
  // Model another tab's new marker before its asynchronous storage event arrives.
  await p.evaluate(()=>localStorage.setItem('priceyard_logout_pending','synthetic-new-logout-marker'));
  const released=p.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/browser/session');await held.fulfill({status:401,contentType:'application/json',body:'{"detail":"Synthetic old session"}'});await released;
  await p.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));assert.equal(await p.evaluate(()=>localStorage.getItem('priceyard_logout_pending')),'synthetic-new-logout-marker');await c.close();
 }
 result.old_bootstrap_401_cannot_acknowledge_new_offline_logout=true;
 {
  const c=await makeContext();await c.addInitScript(()=>Object.defineProperty(navigator,'locks',{value:undefined,configurable:true}));
  const p=await c.newPage();p.setDefaultTimeout(12000);await p.goto(origin+'/login');await p.getByLabel('Email',{exact:true}).fill('trial@example.com');await p.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  let sent=0;p.on('request',r=>{if(new URL(r.url()).pathname==='/api/auth/browser/login')sent++;});await p.getByRole('button',{name:'Log in',exact:true}).click();await p.getByText('Protected browser sessions need an updated browser. Please update your browser and try again.',{exact:true}).waitFor();
  assert.equal(sent,0);assert.equal((await c.cookies()).some(cookie=>cookie.name==='priceyard_local_session'),false);await noJsSecret(p);await c.close();
 }
 result.missing_cross_tab_lock_fails_closed_before_signin=true;
 const report={...result,external_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/cookie-session-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){console.log(JSON.stringify({completed:result,trace,state:debugPage&&!debugPage.isClosed()?await debugPage.evaluate(()=>({url:location.pathname,pending:Boolean(localStorage.getItem('priceyard_logout_pending')),loginSecret:Boolean(localStorage.getItem('priceyard_access_token')),body:document.querySelector('h1')?.textContent})):null,cookie_present:debugContext?((await debugContext.cookies().catch(()=>[])).some(c=>c.name==='priceyard_local_session')):false}));throw error;}finally{await browser.close();}
