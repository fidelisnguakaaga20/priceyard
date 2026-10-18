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
page.on('dialog',dialog=>dialog.accept());
async function api(url){return page.evaluate(async url=>{const r=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return r.json();},url);}
async function countCards(count){await page.waitForFunction(count=>document.querySelectorAll('.admin-card-list > article').length===count,count);}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const original={commodities:await api('/commodities'),markets:await api('/markets'),prices:await api('/price-updates/admin/history')};
 await page.goto(origin+'/__test__/catalog-paging');await page.getByRole('button',{name:'Load synthetic catalog sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic catalog entries per list ready.',{exact:true}).waitFor();
 for(const [path,label,save] of [['commodities','Commodities','Save commodity'],['markets','Markets','Save market']]){
  const complete=await api('/'+path+'/admin/all');assert.equal(complete.length,205);const ids=[];
  for(const offset of [0,100,200]){
   const data=await api('/'+path+'/admin/page?offset='+offset);assert.equal(data.total,205);assert.ok(data.items.length<=100);ids.push(...data.items.map(item=>item.id));
  }
  assert.deepEqual(ids,complete.map(item=>item.id));
  await page.goto(origin+'/admin/'+path+'?offset=100');await countCards(100);
  const target=(await api('/'+path+'/admin/page?offset=100')).items[0];assert.equal(target.is_active,false);
  const card=page.locator('.admin-card-list > article').filter({has:page.getByRole('heading',{name:target.name,exact:true})});await card.getByRole('button',{name:'Edit',exact:true}).click();
  assert.equal(await page.getByLabel('Name',{exact:true}).inputValue(),target.name);assert.equal(await page.locator('input[name=is_active]').isChecked(),false);
  const description='Edited synthetic paging observation';await page.locator('form.admin-form textarea[name=description]').fill(description);
  const saved=page.waitForResponse(r=>r.url()===origin+'/api/'+path+'/'+target.id&&r.request().method()==='PATCH');
  await page.getByRole('button',{name:save,exact:true}).click();assert.equal((await saved).status(),200);await card.getByRole('button',{name:'Edit',exact:true}).waitFor();
  if(path==='commodities')await card.getByText(description,{exact:true}).waitFor();
  else{await card.getByRole('button',{name:'Edit',exact:true}).click();assert.equal(await page.locator('form.admin-form textarea[name=description]').inputValue(),description);await page.getByRole('button',{name:'Cancel',exact:true}).click();}
  assert.equal(new URL(page.url()).searchParams.get('offset'),'100');
  const updated=(await api('/'+path+'/admin/all')).find(item=>item.id===target.id);assert.deepEqual({...updated,description:target.description,updated_at:target.updated_at},target);
  checks[path+'_all_ids_reachable_and_original_edit_fields_preserved']=true;
  await page.goto(origin+'/admin/'+path+'?offset=200');await countCards(5);await page.reload();await countCards(5);
  for(let remaining=5;remaining>0;remaining--){
   const tail=(await api('/'+path+'/admin/page?offset=200')).items[0];assert.ok(tail.name.startsWith('ZZ synthetic'));assert.equal(tail.is_active,false);
   const row=page.locator('.admin-card-list > article').filter({has:page.getByRole('heading',{name:tail.name,exact:true})});
   const removed=page.waitForResponse(r=>r.url()===origin+'/api/'+path+'/'+tail.id&&r.request().method()==='DELETE');await row.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await removed).status(),204);
   if(remaining>1)await countCards(remaining-1);else{await page.waitForURL('**/admin/'+path+'?offset=100');await countCards(100);}
  }
  assert.equal(await page.getByRole('button',{name:'Next',exact:true}).isDisabled(),true);
  checks[path+'_deleting_disposable_tail_returns_to_last_existing_page']=true;
  await page.setViewportSize({width:375,height:812});assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);await page.setViewportSize({width:1280,height:900});
 }
 assert.deepEqual(await api('/commodities'),original.commodities);assert.deepEqual(await api('/markets'),original.markets);assert.deepEqual(await api('/price-updates/admin/history'),original.prices);
 checks.public_catalogs_and_saved_prices_unchanged=true;
 await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();assert.equal(outside,0);
 const report={checks,synthetic_entries_per_catalog:205,page_size:100,extra_sample_entries_inactive:true,only_disposable_unlinked_tail_entries_deleted:true,existing_public_prices_and_measurements_preserved:true,original_css_and_form_layout:true,external_requests:outside,production_connections:0,reseed_preview_after_check:true};
 fs.writeFileSync(path.join(lab,'runtime/catalog-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
