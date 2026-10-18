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
const page=await context.newPage();page.setDefaultTimeout(15000);page.on('dialog',dialog=>dialog.accept());
async function api(url){return page.evaluate(async url=>{const r=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return r.json();},url);}
async function cards(count){await page.waitForFunction(n=>document.querySelectorAll('.admin-card-list > article').length===n,count);}
async function value(name,expected){await page.waitForFunction(({name,expected})=>document.querySelector('form.admin-form [name='+name+']')?.value===expected,{name,expected});}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const original=await api('/price-updates/admin/history');
 await page.goto(origin+'/__test__/signal-paging');await page.getByRole('button',{name:'Load synthetic signal sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic signals per list ready.',{exact:true}).waitFor();
 for(const [endpoint,field,button] of [['market-signals','signal_description','Save market signal'],['quality-signals','risk_note','Save quality signal']]){
  const legacy=await api('/'+endpoint);assert.equal(legacy.length,205);const ids=[];
  for(const offset of [0,100,200]){
   const data=await api('/'+endpoint+'/admin/page?offset='+offset);assert.equal(data.total,205);ids.push(...data.items.map(row=>row.id));
   await page.goto(origin+'/admin/'+endpoint+(offset?'?offset='+offset:''));await cards(data.items.length);
  }
  assert.deepEqual(ids,legacy.map(row=>row.id));checks[endpoint+'_all_ids_reachable']=true;
  await page.reload();await cards(5);await page.getByRole('button',{name:'Previous',exact:true}).click();await page.waitForURL('**offset=100');await cards(100);
  const a=legacy.at(-1),b=legacy.at(-2),form=page.locator('form.admin-form'),id=form.locator('[name=id]');
  await id.fill(String(a.id));await value(field,a[field]);
  for(const key of ['commodity_id','market_id','price_update_id'])assert.equal(await form.locator('[name='+key+']').inputValue(),a[key]==null?'':String(a[key]));
  const changed='Edited synthetic paging observation';await form.locator('[name='+field+']').fill(changed);
  const saved=page.waitForResponse(r=>r.url()===origin+'/api/'+endpoint+'/'+a.id&&r.request().method()==='PATCH');await form.getByRole('button',{name:button,exact:true}).click();assert.equal((await saved).status(),200);await cards(100);
  assert.equal(new URL(page.url()).searchParams.get('offset'),'100');const updated=await api('/'+endpoint+'/'+a.id);
  assert.deepEqual({...updated,[field]:a[field],updated_at:a.updated_at},a);checks[endpoint+'_off_page_edit_preserves_other_fields_and_page']=true;
  await id.fill('');
  let release,entered,finished;const hold=new Promise(resolve=>{release=resolve;}),started=new Promise(resolve=>{entered=resolve;}),done=new Promise(resolve=>{finished=resolve;});
  await context.route(origin+'/api/'+endpoint+'/'+a.id,async route=>{entered();await hold;try{await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(updated)});}catch{}finally{finished();}},{times:1});
  await id.fill(String(a.id));await started;assert.equal(await id.evaluate(input=>input.checkValidity()),false);
  await id.fill(String(b.id));await value(field,b[field]);release();await done;
  assert.equal(await id.inputValue(),String(b.id));assert.equal(await form.locator('[name='+field+']').inputValue(),b[field]);
  checks[endpoint+'_late_off_page_lookup_cannot_overwrite_new_selection']=true;
  await context.route(origin+'/api/'+endpoint+'/1999999',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(updated)}),{times:1});
  await id.fill('1999999');await page.locator('main .status-box.error').filter({hasText:'Record not found.'}).waitFor();assert.equal(await id.evaluate(input=>input.checkValidity()),false);assert.equal(await form.locator('[name='+field+']').inputValue(),'');
  checks[endpoint+'_mismatched_id_response_rejected']=true;await id.fill('');
  await page.goto(origin+'/admin/'+endpoint+'?offset=200');await cards(5);const tail=(await api('/'+endpoint+'/admin/page?offset=200')).items;
  for(let index=0;index<tail.length;index++){
   const card=page.locator('.admin-card-list > article').filter({has:page.locator('.eyebrow',{hasText:new RegExp('(?:^|\\s)#'+tail[index].id+'\\b')})});
   await card.getByRole('button',{name:'Delete',exact:true}).waitFor();
   const removed=page.waitForResponse(r=>r.url()===origin+'/api/'+endpoint+'/'+tail[index].id&&r.request().method()==='DELETE');await card.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await removed).status(),204);
   if(index<4)await cards(4-index);else{await page.waitForURL('**/admin/'+endpoint+'?offset=100');await cards(100);}
  }
  checks[endpoint+'_disposable_tail_delete_returns_to_existing_page']=true;
  await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.setViewportSize({width:1280,height:900});
 }
 assert.deepEqual(await api('/price-updates/admin/history'),original);assert.equal(outside,0);
 const report={checks,records_per_resource:205,page_size:100,existing_price_records_unchanged:true,original_forms_and_mobile_layout:true,external_requests:outside,production_connections:0,reseed_preview_after_check:true};
 fs.writeFileSync(path.join(lab,'runtime/signal-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){console.log(JSON.stringify({url:page.url(),checks,visible_cards:await page.locator('.admin-card-list > article').count()}));throw error;}
finally{await browser.close();}
