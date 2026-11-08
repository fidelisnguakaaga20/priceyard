import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';

const lab=path.dirname(fileURLToPath(import.meta.url));
const origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const checks={},pageErrors=[],routeErrors=[];let outside=0,phase='ordinary form';
function deferred(){let resolve;const promise=new Promise(done=>{resolve=done;});return {promise,resolve};}
function bounded(promise,label){let timer;return Promise.race([promise,new Promise((_,reject)=>{timer=setTimeout(()=>reject(new Error('Timed out: '+label)),12000);})]).finally(()=>clearTimeout(timer));}
async function settle(page){await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
async function login(page,email='free@example.com'){
  const resumed=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/browser/session'&&response.request().method()==='GET');
  await page.goto(origin+'/login');
  if((await resumed).ok()){
    // LoginPage redirects an already authenticated browser to Dashboard.
    // Use the real logout flow before switching accounts in the same profile.
    const loggedOut=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/logout'&&response.request().method()==='POST');
    await page.getByRole('button',{name:'Log out',exact:true}).click();await loggedOut;
    await page.goto(origin+'/login');
  }
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test '+(email.startsWith('free')?'Free':'Paid'),exact:true}).waitFor();
}
// Genuine cookie authentication and matching CSRF/session headers. Never use a
// removed JavaScript bearer credential or Playwright's Node-side API transport.
async function api(page,endpoint,method='GET',body){
  return page.evaluate(async({endpoint,method,body})=>{
    const sessionResponse=await fetch('/api/auth/browser/session',{credentials:'include'});
    if(!sessionResponse.ok)throw new Error('Synthetic browser session unavailable: '+sessionResponse.status);
    const session=await sessionResponse.json();
    const response=await fetch('/api'+endpoint,{method,credentials:'include',headers:{'Content-Type':'application/json','X-PriceYard-Session':session.session_id,'X-PriceYard-CSRF':session.csrf_token},...(body===undefined?{}:{body:JSON.stringify(body)})});
    return {status:response.status,body:response.status===204?null:await response.json()};
  },{endpoint,method,body});
}
async function contextFor(ignoreReadAbort=false){
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
  await context.addInitScript(({ignoreReadAbort})=>{
    localStorage.setItem('priceyard_onboarding_seen','1');
    window.__watchlistCompleted=0;window.__watchlistAborted=0;
    const nativeFetch=window.fetch.bind(window);
    window.fetch=async(input,options={})=>{
      const url=new URL(typeof input==='string'?input:input.url,location.href);
      const watched=url.pathname==='/api/watchlist'&&(options.method||'GET').toUpperCase()==='GET';
      const read=(options.method||'GET').toUpperCase()==='GET'&&['/api/watchlist','/api/commodities','/api/markets','/api/price-updates'].includes(url.pathname);
      if(watched&&options.signal)options.signal.addEventListener('abort',()=>window.__watchlistAborted++,{once:true});
      if(read&&ignoreReadAbort){const {signal,...withoutSignal}=options;options=withoutSignal;}
      try{const response=await nativeFetch(input,options);if(watched)await response.clone().arrayBuffer();return response;}
      finally{if(watched)window.__watchlistCompleted++;}
    };
  },{ignoreReadAbort});
  const page=await context.newPage();page.setDefaultTimeout(12000);page.on('pageerror',error=>pageErrors.push(error.message));
  return {context,page};
}
function card(page,name){return page.locator('.watchlist-grid .card').filter({has:page.getByRole('heading',{name,exact:true})});}
async function fixture(page){
  const before=await api(page,'/watchlist');assert.equal(before.status,200);
  const commodity=(await api(page,'/commodities')).body.find(row=>row.name==='Egusi'&&row.is_active);
  const market=(await api(page,'/markets')).body.find(row=>row.is_active&&!before.body.some(item=>item.commodity_id===null&&item.market_id===row.id));
  assert.ok(commodity&&market,'Existing synthetic commodity and unused market-only choice required');
  assert.ok(!before.body.some(item=>item.commodity_id===commodity.id&&item.market_id===null),'Do not overwrite an existing Egusi selection');
  return {before:before.body,commodity,market};
}
async function create(page,payload,created){const response=await api(page,'/watchlist','POST',payload);assert.equal(response.status,201);created.add(response.body.id);return response.body;}
async function cleanup(page,created,before){
  for(const id of created){const response=await api(page,'/watchlist/'+id,'DELETE');assert.ok([204,404].includes(response.status));}
  const remaining=await api(page,'/watchlist');assert.equal(remaining.status,200);assert.deepEqual(remaining.body,before);
}
async function saveMarket(page,market,created){
  const form=page.locator('form.filter-bar');await form.getByRole('combobox',{name:/^Market/}).selectOption(String(market.id));
  const pending=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/watchlist'&&response.request().method()==='POST');
  await form.getByRole('button',{name:'Save item',exact:true}).click();const response=await pending;assert.equal(response.status(),201);const row=await response.json();created.add(row.id);return row;
}
try{
  // Existing appearance, form actions and persistence, with ordinary AbortSignals.
  {
    const {context,page}=await contextFor(),created=new Set();let f;
    try{
      await login(page);f=await fixture(page);await page.goto(origin+'/watchlist');
      await page.locator('form.filter-bar button').waitFor({state:'visible'});
      await page.waitForFunction(()=>!document.querySelector('form.filter-bar button')?.disabled);
      await saveMarket(page,f.market,created);await card(page,'All commodities').filter({hasText:f.market.name}).waitFor();
      await page.reload();const saved=card(page,'All commodities').filter({hasText:f.market.name});await saved.waitFor();
      const removed=page.waitForResponse(response=>response.request().method()==='DELETE'&&new URL(response.url()).pathname.startsWith('/api/watchlist/'));
      await saved.getByRole('button',{name:'Remove',exact:true}).click();assert.equal((await removed).status(),204);await saved.waitFor({state:'hidden'});
      checks.original_form_save_reload_remove=true;
      assert.ok((await context.cookies()).some(cookie=>cookie.name==='priceyard_local_session'&&cookie.httpOnly));
      checks.http_only_cookie_authentication=true;
    }finally{if(f)await cleanup(page,created,f.before);await context.close();}
  }
  // Ignore GET cancellation deliberately: even a transport which completes an
  // obsolete response must not replace newer successful data, errors or loading.
  for(const staleStatus of [200,503]){
    phase='obsolete list '+staleStatus;
    const {context,page}=await contextFor(true),created=new Set(),held=deferred(),release=deferred();let f;
    try{
      await login(page);f=await fixture(page);const original=await create(page,{commodity_id:f.commodity.id},created);
      await page.goto(origin+'/watchlist');await card(page,'Egusi').waitFor();
      let holdNext=true;
      await page.route(origin+'/api/watchlist',async route=>{
        try{
        if(route.request().method()!=='GET'||!holdNext)return route.continue();
        // Keep all actual HTTP inside the guarded browser. Node-side route.fetch
        // is forbidden by node_guard; the second GET is allowed through below.
        holdNext=false;const response=await api(page,'/watchlist');assert.equal(response.status,200);const snapshot=response.body;
        held.resolve();await release.promise;
        await route.fulfill({status:staleStatus,json:staleStatus===200?snapshot:{detail:'Synthetic obsolete list failure'}});
        }catch(error){routeErrors.push(String(error));held.resolve();await route.abort().catch(()=>{});}
      });
      await saveMarket(page,f.market,created);await bounded(held.promise,'hold post-save reload');
      const removed=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/watchlist/'+original.id&&response.request().method()==='DELETE');
      await card(page,'Egusi').getByRole('button',{name:'Remove',exact:true}).click();assert.equal((await removed).status(),204);
      await card(page,'Egusi').waitFor({state:'hidden'});
      await card(page,'All commodities').filter({hasText:f.market.name}).waitFor();
      const completed=await page.evaluate(()=>window.__watchlistCompleted);release.resolve();
      await page.waitForFunction(previous=>window.__watchlistCompleted>previous,completed);await settle(page);
      checks[staleStatus===200?'obsolete_success_cannot_resurrect_removed_item':'obsolete_failure_cannot_replace_success']=
        await card(page,'Egusi').count()===0&&await page.locator('.status-box.error').count()===0;
      checks['latest_list_and_loader_preserved_after_'+staleStatus]=
        await card(page,'All commodities').filter({hasText:f.market.name}).count()===1&&
        !await page.locator('form.filter-bar button').isDisabled();
    }finally{
      release.resolve();await page.unroute(origin+'/api/watchlist');
      if(f)await cleanup(page,created,f.before);await context.close();
    }
  }
  // A completed old-account mutation may not toast or reload a disposed page.
  {
    phase='old-account mutation';
    const {context,page}=await contextFor(),created=new Set(),held=deferred(),release=deferred();let f,other;
    try{
      await login(page);f=await fixture(page);await page.goto(origin+'/watchlist');
      await page.waitForFunction(()=>!document.querySelector('form.filter-bar button')?.disabled);
      let holdPost=true;
      await page.route(origin+'/api/watchlist',async route=>{
        try{
        if(route.request().method()!=='POST'||!holdPost)return route.continue();
        holdPost=false;
        const response=await api(page,'/watchlist','POST',route.request().postDataJSON());
        assert.equal(response.status,201);created.add(response.body.id);
        held.resolve();await release.promise;await route.fulfill({status:response.status,json:response.body});
        }catch(error){routeErrors.push(String(error));held.resolve();await route.abort().catch(()=>{});}
      });
      await page.locator('form.filter-bar').getByRole('combobox',{name:/^Market/}).selectOption(String(f.market.id));
      await page.getByRole('button',{name:'Save item',exact:true}).click();await bounded(held.promise,'hold old-account mutation');
      other=await context.newPage();other.setDefaultTimeout(12000);await login(other,'paid@example.com');
      await page.evaluate(()=>dispatchEvent(new Event('focus')));
      await page.waitForFunction(()=>document.body.textContent.includes('Test Paid'));
      let lateReads=0;const count=request=>{if(new URL(request.url()).pathname==='/api/watchlist'&&request.method()==='GET')lateReads++;};
      page.on('request',count);const pending=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/watchlist'&&response.request().method()==='POST');
      release.resolve();await pending;await settle(page);
      checks.old_account_save_has_no_new_account_toast=await page.locator('.toast-message').filter({hasText:'Added to your watchlist.'}).count()===0;
      checks.old_account_save_does_not_reload_disposed_page=lateReads===0;
      page.off('request',count);
    }finally{
      release.resolve();await page.unroute(origin+'/api/watchlist');
      if(f){const cleaner=other||page;await login(cleaner);await cleanup(cleaner,created,f.before);}
      await context.close();
    }
  }
  assert.equal(outside,0);assert.deepEqual(pageErrors,[]);assert.deepEqual(routeErrors,[]);
  const failures=Object.entries(checks).filter(([,passed])=>!passed).map(([name])=>name);
  const report={checks,failures,expected_original_bug:expectBug,production_connections:0,external_page_requests:outside,page_errors:pageErrors};
  fs.writeFileSync(path.join(lab,'runtime/watchlist-race-'+(expectBug?'before':'after')+'.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
  if(expectBug)assert.ok(failures.includes('obsolete_success_cannot_resurrect_removed_item'),'Original stale-list bug must be reproduced');
  else assert.deepEqual(failures,[]);
}catch(error){
  const failure={phase,error:String(error),checks,routeErrors,pageErrors,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/watchlist-race-last-error.json'),JSON.stringify(failure,null,2));
  console.error(JSON.stringify(failure));throw error;
}finally{await browser.close();}
