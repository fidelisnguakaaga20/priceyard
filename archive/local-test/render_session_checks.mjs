// Original React + original API behind the proposed route, with no network.
// This validates the application, not Render's edge implementation.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {spawn} from 'node:child_process';
import readline from 'node:readline';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(lab,'../..');
const front='https://priceyard.onrender.com';
const manifest=JSON.parse(fs.readFileSync(path.join(lab,'runtime/frontend.json'),'utf8'));
const snapshot=path.resolve(manifest.path),dist=path.join(snapshot,'dist');
assert.equal(manifest.purpose,'synthetic-only-no-application-credentials');
assert.equal(path.dirname(snapshot),path.join(lab,'runtime'));
const {chromium}=await import(pathToFileURL(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const bridge=spawn(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/venv/Scripts/python.exe'),[path.join(lab,'render_session_bridge.py')],{cwd:lab,env:process.env,stdio:['pipe','pipe','pipe']});
let next=0,readyResolve,readyReject,browser,context;
const pending=new Map(),ready=new Promise((resolve,reject)=>{readyResolve=resolve;readyReject=reject;});
const lines=readline.createInterface({input:bridge.stdout});
lines.on('line',line=>{try{const message=JSON.parse(line);if(message.ready)readyResolve();else{const task=pending.get(message.id);if(task){pending.delete(message.id);clearTimeout(task.timer);task.resolve(message);}}}catch{readyReject(Error('Invalid synthetic bridge response'));}});
bridge.on('error',readyReject);
bridge.on('exit',code=>{readyReject(Error('Synthetic bridge exited: '+code));for(const task of pending.values()){clearTimeout(task.timer);task.reject(Error('Synthetic bridge stopped'));}pending.clear();});
bridge.stderr.resume();
const report={scope:'local virtual HTTPS original React and real API; NOT Render edge certification',production_requests:0,providers_contacted:0,cases:{}};
const deadline=setTimeout(()=>{readyReject(Error('Synthetic bridge startup timeout'));bridge.kill();},20000);
try{
 await ready;clearTimeout(deadline);
 browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
 context=await browser.newContext({serviceWorkers:'block'});
 await context.addInitScript(()=>{localStorage.setItem('priceyard_onboarding_seen','1');localStorage.setItem('priceyard_onboarding_dismissed','1');});
 await context.route('**/*',async route=>{
  const request=route.request(),url=new URL(request.url());
  if(url.origin!==front)return route.abort();
  if(url.pathname.startsWith('/api/')){
   const id=++next;
   const response=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>{pending.delete(id);reject(Error('Synthetic request timeout'));},12000);pending.set(id,{resolve,reject,timer});request.allHeaders().then(headers=>bridge.stdin.write(JSON.stringify({id,url:request.url(),method:request.method(),headers,body:(request.postDataBuffer()||Buffer.alloc(0)).toString('base64')})+'\n')).catch(reject);});
   const headers={};for(const [name,value]of response.headers){if(['content-length','transfer-encoding','content-encoding'].includes(name.toLowerCase()))continue;headers[name]=headers[name]?headers[name]+'\n'+value:value;}
   return route.fulfill({status:response.status,headers,body:Buffer.from(response.body,'base64')});
  }
  let file=path.resolve(dist,'.'+decodeURIComponent(url.pathname));
  if(file!==dist&&!file.startsWith(dist+path.sep))return route.abort();
  if(!fs.existsSync(file)||!fs.statSync(file).isFile())file=path.join(dist,'index.html');
  const mime={'.html':'text/html','.js':'application/javascript','.css':'text/css','.svg':'image/svg+xml','.json':'application/json','.png':'image/png','.webmanifest':'application/manifest+json'}[path.extname(file)]||'application/octet-stream';
  return route.fulfill({status:200,contentType:mime,body:fs.readFileSync(file)});
 });
 const page=await context.newPage();page.setDefaultTimeout(12000);
 await page.goto(front+'/login');
 await page.getByLabel('Email',{exact:true}).fill('routing@example.com');
 await page.getByLabel('Password',{exact:true}).fill('SyntheticRouting8!');
 const login=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/browser/login');
 await page.getByRole('button',{name:'Log in',exact:true}).click();
 assert.equal((await login).status(),200);
 await page.waitForURL(front+'/dashboard');
 await page.getByRole('heading',{name:'Welcome, Synthetic Routing',exact:true}).waitFor();
 const cookie=(await context.cookies()).find(c=>c.name==='__Host-priceyard_session');
 assert.ok(cookie?.secure&&cookie.httpOnly&&cookie.sameSite==='Lax');
 assert.equal(cookie.domain,'priceyard.onrender.com');
 assert.equal(await page.evaluate(()=>document.cookie.includes('__Host-priceyard_session')),false);
 report.cases.original_login_dashboard_secure_host_cookie=true;
 await page.reload();await page.getByRole('heading',{name:'Welcome, Synthetic Routing',exact:true}).waitFor();
 const checks=await page.evaluate(async()=>{
  const session=await fetch('/api/auth/browser/session',{credentials:'include'}),meta=await session.json();
  const bad=await fetch('/api/auth/logout',{method:'POST',credentials:'include'});
  const wrong=await fetch('/api/auth/logout',{method:'POST',credentials:'include',headers:{'X-PriceYard-Session':meta.session_id,'X-PriceYard-CSRF':'wrong'}});
  const me=await fetch('/api/auth/me',{credentials:'include'});
  const missing=await fetch('/api/not-a-real-route');
  return {session:session.status,cache:session.headers.get('cache-control'),missingCSRF:bad.status,wrongCSRF:wrong.status,me:me.status,missingAPI:missing.status,missingAPIType:missing.headers.get('content-type')};
 });
 assert.equal(checks.session,200);assert.equal(checks.cache,'private, no-store');assert.equal(checks.missingCSRF,403);assert.equal(checks.wrongCSRF,403);assert.equal(checks.me,200);assert.equal(checks.missingAPI,404);assert.match(checks.missingAPIType,/application\/json/);
 report.cases.reload_API_requests_CSRF_and_private_cache=true;
 const other=await browser.newContext({serviceWorkers:'block'});
 await other.route('**/*',r=>r.abort());
 assert.equal((await other.cookies()).length,0);await other.close();
 const logout=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/auth/logout'&&r.request().method()==='POST');
 await page.getByRole('button',{name:'Log out',exact:true}).click();assert.equal((await logout).status(),204);
 assert.equal((await context.cookies()).some(c=>c.name==='__Host-priceyard_session'),false);
 const after=await page.evaluate(async token=>({session:(await fetch('/api/auth/browser/session',{credentials:'include'})).status,replay:(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status}),cookie.value);
 assert.deepEqual(after,{session:401,replay:401});
 report.cases.logout_deletion_and_server_revocation=true;
 report.status='PASS_local_application_routing';
}catch(error){report.status='FAIL';report.error_type=error.name;report.error=error.message;process.exitCode=1;}
finally{
 clearTimeout(deadline);
 if(context)await context.close();if(browser)await browser.close();
 bridge.stdin.end();
 await Promise.race([new Promise(resolve=>bridge.once('exit',resolve)),new Promise(resolve=>setTimeout(()=>{if(bridge.exitCode===null)bridge.kill();resolve();},3000))]);
 fs.writeFileSync(path.join(lab,'runtime/render-session-checks.json'),JSON.stringify(report,null,2));
 process.stdout.write(JSON.stringify(report)+'\n');
}
