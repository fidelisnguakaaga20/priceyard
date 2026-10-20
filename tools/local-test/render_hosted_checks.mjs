// Real HTTPS requests ONLY to the pinned temporary Render static site.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(lab,'../..');
const run=path.join(lab,'runtime/render-hosted-20261020');
const state=JSON.parse(fs.readFileSync(path.join(run,'state.json'),'utf8'));
const origin='https://priceyard-py35-check-20261020.onrender.com';
assert.equal(state.origin,origin);assert.equal(state.status,'awaiting_test_only_rewrite');
assert.ok(state.expires_at_epoch*1000>Date.now());
const {chromium}=await import(pathToFileURL(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
let browser,context;const report={status:'FAIL',scope:'actual Render edge, synthetic original API',cases:{},production_requests:0};
const deadline=setTimeout(()=>{if(browser)void browser.close();},90000);
async function makeContext(){const c=await browser.newContext({serviceWorkers:'block'});await c.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());return c;}
function privateCache(value){const parts=(value||'').toLowerCase().split(',').map(p=>p.trim());assert.ok(parts.includes('private')&&parts.includes('no-store')&&!parts.includes('public'));}
try{
 browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
 context=await makeContext();const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin,{waitUntil:'domcontentloaded'});
 assert.match(await page.title(),/PriceYard isolated route check/);
 const health=await page.evaluate(async()=>{const r=await fetch('/api/health',{cache:'no-store'});return {status:r.status,body:await r.text()};});
 assert.equal(health.status,200,'Test rewrite did not reach the synthetic API');
 assert.equal(JSON.parse(health.body).proof,state.proof,'Wrong target: no login request will be sent');
 report.cases.synthetic_target_identity=true;
 const raw='{\n  "synthetic": true\n}';
 const probe=await page.evaluate(async body=>{const r=await fetch('/api/probe?one=a%20b&one=c',{method:'POST',body,credentials:'include',cache:'no-store'});return {status:r.status,cache:r.headers.get('cache-control'),body:await r.text()};},raw);
 report.probe_status=probe.status;
 assert.equal(probe.status,207,'Render did not preserve the synthetic POST; login not attempted');
 const payload=JSON.parse(probe.body);assert.equal(payload.method,'POST');assert.equal(payload.query,'one=a%20b&one=c');assert.equal(payload.body_sha256,crypto.createHash('sha256').update(raw).digest('hex'));privateCache(probe.cache);
 const cookies=await context.cookies();for(const name of ['__Host-py_route_one','__Host-py_route_two'])assert.ok(cookies.some(c=>c.name===name&&c.secure&&c.httpOnly&&c.domain===new URL(origin).hostname));
 report.cases.POST_body_query_status_multiple_cookies_private_cache=true;
 const login=await page.evaluate(async()=>{const r=await fetch('/api/auth/browser/login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:'routing@example.com',password:'SyntheticRouting8!',remember:true})});return {status:r.status,body:await r.json(),cache:r.headers.get('cache-control')};});
 assert.equal(login.status,200);privateCache(login.cache);
 const cookie=(await context.cookies()).find(c=>c.name==='__Host-priceyard_session');assert.ok(cookie?.secure&&cookie.httpOnly&&cookie.sameSite==='Lax');
 assert.equal(cookie.domain,new URL(origin).hostname);
 assert.equal(await page.evaluate(()=>document.cookie.includes('__Host-priceyard_session')),false);
 await page.reload();
 const session=await page.evaluate(async()=>{const r=await fetch('/api/auth/browser/session',{credentials:'include',cache:'no-store'});return {status:r.status,cache:r.headers.get('cache-control'),body:await r.json()};});
 assert.equal(session.status,200);privateCache(session.cache);assert.deepEqual(session.body,login.body);
 const other=await makeContext();const guest=await other.newPage();await guest.goto(origin);
 const guestStatus=await guest.evaluate(async()=>(await fetch('/api/auth/browser/session',{credentials:'include'})).status);assert.equal(guestStatus,401);await other.close();
 const checks=await page.evaluate(async meta=>{const headers={'X-PriceYard-Session':meta.session_id,'X-PriceYard-CSRF':'wrong'};const bad=await fetch('/api/auth/logout',{method:'POST',credentials:'include'});const wrong=await fetch('/api/auth/logout',{method:'POST',headers,credentials:'include'});const me=await fetch('/api/auth/me',{credentials:'include'});const absent=await fetch('/api/not-a-real-route');return {missing:bad.status,wrong:wrong.status,me:me.status,type:absent.headers.get('content-type'),absent:absent.status};},session.body);
 assert.equal(checks.missing,403);assert.equal(checks.wrong,403);assert.equal(checks.me,200);assert.equal(checks.absent,404);assert.match(checks.type,/application\/json/);
 report.cases.login_cookie_reload_API_CSRF_private_client_isolation=true;
 const logout=await page.evaluate(async meta=>(await fetch('/api/auth/logout',{method:'POST',credentials:'include',headers:{'X-PriceYard-Session':meta.session_id,'X-PriceYard-CSRF':meta.csrf_token}})).status,session.body);
 assert.equal(logout,204);assert.equal((await context.cookies()).some(c=>c.name==='__Host-priceyard_session'),false);
 const after=await page.evaluate(async token=>({session:(await fetch('/api/auth/browser/session',{credentials:'include'})).status,replay:(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status}),cookie.value);assert.deepEqual(after,{session:401,replay:401});
 report.cases.logout_deletion_and_revocation=true;
 await page.goto(origin+'/dashboard');assert.match(await page.title(),/PriceYard isolated route check/);report.cases.SPA_fallback=true;
 report.status='PASS';
}catch(error){report.error_type=error.name;report.error=error.message;}
finally{clearTimeout(deadline);if(context)await context.close();if(browser)await browser.close();fs.writeFileSync(path.join(run,'browser-result.json'),JSON.stringify(report,null,2));process.stdout.write(JSON.stringify(report)+'\n');}
