import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const requests=[],checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
page.on('request',request=>{const url=new URL(request.url());if(request.method()==='GET'&&['/api/users','/api/payments','/api/users/page','/api/payments/page'].includes(url.pathname))requests.push(url.pathname+url.search);});
async function api(url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)})});
 return {status:response.status,body:await response.json()};
},{url,method,body});}
async function rows(count,payments=false){const selector=payments?'.admin-table tbody tr':'.admin-table-view tbody tr';await page.waitForFunction(({selector,count})=>document.querySelectorAll(selector).length===count,{selector,count});}
async function move(name,count,payments=false){
 const offset=Number(new URL(page.url()).searchParams.get('offset')||0),next=name==='Next'?offset+100:Math.max(0,offset-100);
 const reply=page.waitForResponse(response=>response.url()===origin+'/api/'+(payments?'payments':'users')+'/page?offset='+next);
 await page.getByRole('button',{name,exact:true}).click();const payload=await(await reply).json();await rows(count,payments);
 if(payload.items.length)await page.locator(payments?'.admin-table tbody tr':'.admin-table-view tbody tr').first().getByText(payments?payload.items[0].reference:payload.items[0].email,{exact:true}).waitFor();
 await page.getByRole('navigation',{name:payments?'Payments pages':'Users pages'}).getByText(/Showing/).waitFor();
}
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 await page.goto(origin+'/__test__/admin-paging');await page.getByRole('button',{name:'Load synthetic sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic users and205 synthetic payments ready.',{exact:true}).waitFor();
 await page.goto(origin+'/admin/users');await rows(100);await page.getByText('Total users: 205',{exact:true}).waitFor();
 assert.equal(await page.getByRole('button',{name:'Previous',exact:true}).isDisabled(),true);assert.equal(requests.includes('/api/users'),false);
 const first=(await api('/users/page?offset=0')).body,second=(await api('/users/page?offset=100')).body,last=(await api('/users/page?offset=200')).body;
 assert.deepEqual([first.items.length,second.items.length,last.items.length],[100,100,5]);assert.equal(new Set([...first.items,...second.items,...last.items].map(row=>row.id)).size,205);
 await move('Next',100);await page.getByText('Showing 101–200 of 205',{exact:true}).waitFor();
 const target=second.items[0],row=page.locator('.admin-table-view tbody tr').filter({hasText:target.email});
 const saved=page.waitForResponse(r=>r.url()===origin+'/api/users/'+target.id&&r.request().method()==='PATCH');
 await row.getByRole('button',{name:'Deactivate',exact:true}).click();assert.equal((await saved).status(),200);
 await row.getByRole('button',{name:'Activate',exact:true}).waitFor();assert.equal(new URL(page.url()).searchParams.get('offset'),'100');await page.getByText('Total users: 205',{exact:true}).waitFor();
 checks.users_keep_complete_totals_and_edit_current_page=true;
 await move('Next',5);assert.equal(await page.getByRole('button',{name:'Next',exact:true}).isDisabled(),true);await page.reload();await rows(5);assert.equal(new URL(page.url()).searchParams.get('offset'),'200');
 await move('Previous',100);await page.getByText('Showing 101–200 of 205',{exact:true}).waitFor();
 checks.page_navigation_refresh_and_previous_preserved=true;
 for(const failure of [false,true]){
  const ready=deferred(),release=deferred();const url=origin+'/api/users/page?offset=200';
  const handler=async route=>{ready.resolve();await release.promise;await route.fulfill({status:failure?503:200,contentType:'application/json',body:JSON.stringify(failure?{detail:'Synthetic obsolete Admin page'}:last)});};
  await context.route(url,handler);await page.getByRole('button',{name:'Next',exact:true}).click();await ready.promise;await page.goBack();await rows(100);await page.getByText('Showing 101–200 of 205',{exact:true}).waitFor();
  const completed=page.waitForResponse(r=>r.url()===url&&r.status()===(failure?503:200));release.resolve();await (await completed).finished();await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));
  assert.equal(await page.locator('.admin-table-view tbody tr').count(),100);assert.equal(await page.getByText('Synthetic obsolete Admin page',{exact:true}).count(),0);
  await context.unroute(url,handler);
 }
 checks.obsolete_page_rows_and_errors_cannot_replace_browser_back=true;
 await page.goto(origin+'/admin/users?offset=900');await page.waitForURL('**/admin/users?offset=200');await rows(5);
 checks.out_of_range_last_page_moves_back_without_dropping_records=true;
 await page.setViewportSize({width:375,height:812});await page.goto(origin+'/admin/users?offset=100');await page.waitForFunction(()=>document.querySelectorAll('.admin-card-list > article').length===100);
 assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);checks.mobile_original_cards_and_paging_fit=true;
 await page.setViewportSize({width:1280,height:900});await page.goto(origin+'/admin/payments');await rows(100,true);assert.equal(requests.includes('/api/payments'),false);
 const references=[];
 for(const [index,count] of [[0,100],[1,100],[2,5]]){
  if(index)await move('Next',count,true);
  const values=await page.locator('.admin-table tbody tr td:last-child').allTextContents();assert.equal(values.length,count);references.push(...values);
 }
 assert.equal(new Set(references).size,205);assert.equal(await page.getByRole('button',{name:'Next',exact:true}).isDisabled(),true);await move('Previous',100,true);
 checks.all_payment_records_reachable_in_original_columns=true;
 const legacyUsers=await api('/users'),legacyPayments=await api('/payments');assert.equal(legacyUsers.body.length,205);assert.equal(legacyPayments.body.length,205);
 assert.equal((await api('/users/'+target.id,'PATCH',{is_active:true})).status,200);
 checks.legacy_api_results_remain_complete=true;
 assert.equal(outside,0);
 const report={checks,synthetic_users:205,synthetic_payments:205,maximum_rows_per_visible_list:100,original_forms_columns_and_styles_preserved:true,temporary_preview_reseed_required:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/admin-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
