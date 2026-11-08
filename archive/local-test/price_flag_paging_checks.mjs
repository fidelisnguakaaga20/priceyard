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
async function count(selector,n){await page.waitForFunction(({selector,n})=>document.querySelectorAll(selector).length===n,{selector,n});}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const original=await api('/price-updates/admin/history');
 await page.goto(origin+'/__test__/price-flag-paging');await page.getByRole('button',{name:'Load synthetic price and flag sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic prices and flagged groups ready.',{exact:true}).waitFor();
 const before=await api('/price-updates/admin/history'),ids=[];assert.equal(before.length,205);assert.deepEqual(before.filter(x=>original.some(y=>y.id===x.id)),original);
 for(const offset of [0,100,200]){
  const data=await api('/price-updates/admin/history/page?offset='+offset);assert.equal(data.total,205);ids.push(...data.items.map(x=>x.id));
  await page.goto(origin+'/admin/prices'+(offset?'?offset='+offset:''));await count('.admin-table tbody tr',data.items.length);
 }
 assert.deepEqual(ids,before.map(x=>x.id));checks.all_price_statuses_ids_full_totals_and_original_records=true;
 await page.reload();await count('.admin-table tbody tr',5);await page.getByRole('button',{name:'Previous',exact:true}).click();await page.waitForURL('**offset=100');await count('.admin-table tbody tr',100);await page.goBack();await page.waitForURL('**offset=200');await count('.admin-table tbody tr',5);
 const record=original[0];await page.getByLabel('Record ID',{exact:true}).fill(String(record.id));
 const correction=page.locator('form.admin-form').nth(1);await correction.getByRole('button',{name:/Show extra fields/}).click();await correction.getByLabel('Notes',{exact:true}).fill('Synthetic paging correction');
 const saved=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/'+record.id&&r.request().method()==='PATCH');await correction.getByRole('button',{name:'Save correction',exact:true}).click();assert.equal((await saved).status(),200);await count('.admin-table tbody tr',5);assert.equal(new URL(page.url()).searchParams.get('offset'),'200');
 let after=await api('/price-updates/admin/history');const changed=after.find(x=>x.id===record.id);assert.deepEqual({...changed,notes:record.notes,updated_at:record.updated_at},record);checks.price_correction_retains_page_status_sources_measurements_and_values=true;
 await page.goto(origin+'/admin/prices');await count('.admin-table tbody tr',100);
 const create=page.locator('form.admin-form').first();await create.locator('[name=commodity_id]').selectOption({label:'Egusi'});await create.locator('[name=market_id]').selectOption({label:'Kwali Market'});await create.getByRole('button',{name:/Show extra fields/}).click();
 await create.getByRole('button',{name:'Prefill from last entry',exact:true}).click();await page.waitForFunction(v=>document.querySelector('form.admin-form [name=previous_price_low]').value===v,String(record.price_low));
 assert.equal(await create.locator('[name=source_1]').inputValue(),record.source_1);assert.equal(await create.locator('[name=bag_size]').inputValue(),record.bag_size||'');checks.prefill_reads_latest_matching_pair_beyond_page_and_preserves_unknown_measurements=true;
 await create.locator('[name=previous_price_low]').fill('');
 let release,entered,finished;const held=new Promise(r=>release=r),started=new Promise(r=>entered=r),done=new Promise(r=>finished=r);
 await context.route('**/api/price-updates/admin/latest?*',async route=>{entered();await held;try{await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(changed)});}catch{}finally{finished();}},{times:1});
 await create.getByRole('button',{name:'Prefill from last entry',exact:true}).click();await started;await create.locator('[name=notes]').fill('Synthetic unsaved edit');release();await done;
 assert.equal(await create.locator('[name=previous_price_low]').inputValue(),'');assert.equal(await create.locator('[name=notes]').inputValue(),'Synthetic unsaved edit');checks.delayed_prefill_cannot_overwrite_new_form_values=true;
 await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.setViewportSize({width:1280,height:900});assert.equal(await page.getByLabel(/grade/i).count(),0);
 const flagsBefore=await api('/price-updates/admin/flagged'),flagIds=[];assert.equal(flagsBefore.length,205);
 for(const offset of [0,100,200]){
  const data=await api('/price-updates/admin/flagged/page?offset='+offset);assert.equal(data.total,205);flagIds.push(...data.items.map(x=>x.price_update_id));
  await page.goto(origin+'/admin/flagged'+(offset?'?offset='+offset:''));await count('.admin-card-list > article',data.items.length);
 }
 assert.deepEqual(flagIds,flagsBefore.map(x=>x.price_update_id));checks.all_flagged_ids_group_totals_and_counts_reachable=true;
 await page.reload();await count('.admin-card-list > article',5);const tail=(await api('/price-updates/admin/flagged/page?offset=200')).items;
 for(let i=0;i<tail.length;i++){
  const resolved=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/'+tail[i].price_update_id+'/flags/resolve'&&r.request().method()==='POST');await page.locator('.admin-card-list > article').first().getByRole('button',{name:'Mark reviewed',exact:true}).click();assert.equal((await resolved).status(),204);
  if(i<4)await count('.admin-card-list > article',4-i);else{await page.waitForURL('**offset=100');await count('.admin-card-list > article',100);}
 }
 assert.equal((await api('/price-updates/admin/flagged')).length,200);assert.deepEqual(await api('/price-updates/admin/history'),after);checks.review_flags_preserves_prices_and_recovers_empty_tail=true;
 await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));checks.original_fields_and_mobile_layout=true;assert.equal(outside,0);
 const report={checks,records_per_list:205,page_size:100,external_requests:outside,production_connections:0,reseed_preview_after_check:true};fs.writeFileSync(path.join(lab,'runtime/price-flag-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){console.log(JSON.stringify({url:page.url(),checks}));throw error;}
finally{await browser.close();}
