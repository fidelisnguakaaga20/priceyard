import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectOld=process.argv.includes('--expect-bug');let outside=0;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
const paths=['/users','/commodities/admin/all','/markets/admin/all','/price-updates','/price-updates/admin/history','/subscriptions','/feedback/summary','/feedback','/payments'];
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
 const expected=await page.evaluate(async paths=>{
  const token=localStorage.getItem('priceyard_access_token'),headers={Authorization:'Bearer '+token};
  const [users,commodities,markets,latest,history,subscriptions,feedback,feedbackList,payments]=await Promise.all(paths.map(async path=>{const response=await fetch('/api'+path,{headers});if(!response.ok)throw Error('Local baseline read failed');return response.json();}));
  const successful=payments.filter(p=>p.status==='success');
  return {'Total users':String(users.length),'Commodities':String(commodities.length),'Markets':String(markets.length),'Latest updates':String(latest.length),'Outdated prices':String(history.filter(p=>p.is_outdated).length),'Trial users':String(subscriptions.filter(p=>p.status==='trial').length),'Active users':String(users.filter(u=>u.is_active).length),'Feedback count':String(feedback.count),'Average rating':feedback.average_rating==null?'—':feedback.average_rating.toFixed(2),'New users (7 days)':String(users.filter(u=>new Date(u.created_at).getTime()>=Date.now()-7*86400000).length),'Referrals used':String(users.filter(u=>u.referred_by_id!==null).length),'Testimonials live':String(feedbackList.filter(f=>f.is_public_testimonial).length),'Successful payments':String(successful.length),'Revenue (NGN)':successful.reduce((sum,p)=>sum+Number(p.amount),0).toLocaleString('en-NG')};
 },paths);
 const requests=[];page.on('request',request=>{const url=new URL(request.url());if(url.pathname.startsWith('/api/'))requests.push(url.pathname.slice(4));});
 await page.goto(origin+'/admin');await page.waitForFunction(()=>document.querySelectorAll('.admin-metric').length===14);
 const actual=await page.locator('.admin-metric').evaluateAll(cards=>Object.fromEntries(cards.map(card=>[card.querySelector('span').textContent,card.querySelector('strong').textContent])));
 assert.deepEqual(actual,expected);
 assert.equal(paths.filter(path=>requests.includes(path)).length,expectOld?9:0);
 assert.equal(requests.filter(path=>path==='/admin/summary').length,expectOld?0:1);
 let recovery=null;
 if(!expectOld){
  await context.route('**/api/admin/summary',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic dashboard outage'})}));
  await page.reload();await page.locator('.status-box.error').getByText('Synthetic dashboard outage').waitFor();assert.equal(await page.locator('.admin-metric').count(),0);
  await context.unroute('**/api/admin/summary');await page.reload();await page.waitForFunction(()=>document.querySelectorAll('.admin-metric').length===14);recovery=true;
 }
 assert.equal(outside,0);
 const report={fourteen_original_labels_and_values_preserved:true,initial_dashboard_list_requests:paths.filter(path=>requests.includes(path)).length,initial_summary_requests:expectOld?0:1,outage_reload_recovers:recovery,original_implementation:expectOld,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/dashboard-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
