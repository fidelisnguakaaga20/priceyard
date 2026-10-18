import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url){return page.evaluate(async url=>{const r=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return r.json();},url);}
async function rows(count){await page.waitForFunction(n=>document.querySelectorAll('.admin-table tbody tr').length===n,count);}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const prices=await api('/price-updates/admin/history');
 await page.goto(origin+'/__test__/subscription-paging');await page.getByRole('button',{name:'Load synthetic subscription sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic subscriptions ready.',{exact:true}).waitFor();
 await page.goto(origin+'/admin/subscriptions');await rows(100);
 const before=await api('/subscriptions'),ids=[];assert.equal(before.length,205);
 for(const offset of [0,100,200]){
  const data=await api('/subscriptions/admin/page?offset='+offset);assert.equal(data.total,205);ids.push(...data.items.map(x=>x.id));
  await page.goto(origin+'/admin/subscriptions'+(offset?'?offset='+offset:''));await rows(data.items.length);
  assert.equal(await page.getByRole('button',{name:'Previous',exact:true}).isDisabled(),offset===0);
  assert.equal(await page.getByRole('button',{name:'Next',exact:true}).isDisabled(),offset===200);
 }
 assert.deepEqual(ids,before.map(x=>x.id));checks.all_ids_ascending_order_full_totals_and_page_bounds=true;
 await page.reload();await rows(5);await page.getByRole('button',{name:'Previous',exact:true}).click();await page.waitForURL('**offset=100');await rows(100);
 await page.goBack();await page.waitForURL('**offset=200');await rows(5);checks.reload_previous_and_browser_back=true;
 const tail=(await api('/subscriptions/admin/page?offset=200')).items,record=tail.find(x=>x.status==='expired');assert.ok(record);
 const select=page.getByLabel('Subscription status for user #'+record.user_id,{exact:true});
 const saved=page.waitForResponse(r=>r.url()===origin+'/api/subscriptions/'+record.user_id+'/status'&&r.request().method()==='PATCH');await select.selectOption('trial');assert.equal((await saved).status(),200);await page.locator('.status-box.success').getByText('Subscription for user #'+record.user_id+' updated.',{exact:true}).waitFor();await rows(5);
 assert.equal(new URL(page.url()).searchParams.get('offset'),'200');await page.reload();await rows(5);assert.equal(await select.inputValue(),'trial');
 const after=await api('/subscriptions'),changed=after.find(x=>x.id===record.id);
 assert.equal((Date.parse(changed.trial_ends_at)-Date.parse(changed.trial_started_at))/(24*60*60*1000),14);
 assert.deepEqual(after.filter(x=>x.id!==record.id),before.filter(x=>x.id!==record.id));checks.original_status_action_retains_page_14_day_trial_and_other_records=true;
 await page.getByRole('button',{name:'Send trial-expiry reminders',exact:true}).waitFor();
 assert.deepEqual(await page.locator('.admin-table thead th').allTextContents(),['User','Plan','Status','Trial ends']);
 await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks.original_columns_controls_and_mobile_layout=true;
 assert.deepEqual(await api('/price-updates/admin/history'),prices);assert.equal(outside,0);
 const report={checks,records:205,page_size:100,existing_price_records_unchanged:true,external_requests:outside,production_connections:0,reseed_preview_after_check:true};
 fs.writeFileSync(path.join(lab,'runtime/subscription-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){console.log(JSON.stringify({url:page.url(),checks,rows:await page.locator('.admin-table tbody tr').count()}));throw error;}
finally{await browser.close();}
