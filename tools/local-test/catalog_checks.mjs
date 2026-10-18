import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let outside=0;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function read(url){return page.evaluate(async url=>{
 const response=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!response.ok)throw Error('Synthetic read failed');return response.json();
},url);}
function historyValues(rows){return rows.map(({commodity,market,...values})=>values);}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
 const originalHistory=historyValues(await read('/price-updates/admin/history')),auditIds=(await read('/audit-logs')).map(row=>row.id);
 for(const [kind,plural,name] of [['commodity','commodities','Egusi'],['market','markets','Kwali Market']]){
  const original=(await read('/'+plural+'/admin/all')).find(row=>row.name===name);assert.ok(original);
  await page.goto(origin+'/admin/'+plural);const card=page.locator('.admin-card-list article').filter({has:page.getByRole('heading',{name,exact:true})});await card.waitFor();
  for(const description of ['Synthetic local description check',original.description||'']){
   await card.getByRole('button',{name:'Edit',exact:true}).click();const form=page.locator('form.admin-form');
   await form.locator('textarea[name="description"]').fill(description);
   const saved=page.waitForResponse(r=>r.url()===origin+'/api/'+plural+'/'+original.id&&r.request().method()==='PATCH');
   const reloaded=page.waitForResponse(r=>r.url()===origin+'/api/'+plural+'/admin/page?offset=0');
   await form.getByRole('button',{name:'Save '+kind,exact:true}).click();assert.equal((await saved).status(),200);await (await reloaded).finished();await card.waitFor();
   await page.waitForFunction(()=>!document.querySelector('button:disabled'));
  }
  const preserved=(await read('/'+plural+'/admin/all')).find(row=>row.id===original.id);
  const {updated_at:oldTime,...oldFields}=original,{updated_at:newTime,...newFields}=preserved;assert.deepEqual(newFields,oldFields);
  page.once('dialog',dialog=>dialog.accept());const denied=page.waitForResponse(r=>r.url()===origin+'/api/'+plural+'/'+original.id&&r.request().method()==='DELETE');
  await card.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await denied).status(),409);
  await page.locator('.status-box.error').getByText(/referenced by existing records/).waitFor();await page.reload();await card.waitFor();
  const createForm=page.locator('form.admin-form');
  await createForm.locator('input[name="name"]').fill('  '+name.toUpperCase()+'  ');
  if(kind==='market')await createForm.locator('input[name="state"]').fill(original.state||'');
  const [duplicate]=await Promise.all([
   page.waitForResponse(r=>r.url()===origin+'/api/'+plural&&r.request().method()==='POST'),
   createForm.getByRole('button',{name:'Create '+kind,exact:true}).click(),
  ]);
  assert.equal(duplicate.status(),409);
  await page.locator('.status-box.error').getByText(/already exists/).waitFor();
 }
 assert.deepEqual(historyValues(await read('/price-updates/admin/history')),originalHistory);
 const audits=(await read('/audit-logs')).filter(row=>!auditIds.includes(row.id)).sort((a,b)=>a.id-b.id);
 for(const kind of ['commodity','market']){const logs=audits.filter(row=>row.action===kind+'.edit');assert.equal(logs.length,2);assert.deepEqual(logs[1].old_value,logs[0].new_value);}
 assert.equal(audits.length,4);assert.equal(outside,0);
 const report={original_commodity_and_market_edit_controls:true,original_names_ids_fields_and_descriptions_preserved:true,referenced_delete_still_denied:true,case_whitespace_duplicates_show_original_conflict_without_saving:true,complete_price_history_preserved:true,four_continuous_audit_records:true,new_catalog_records:0,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/catalog-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){
 console.log(JSON.stringify({url:page.url(),headings:await page.locator('h1,h2,h3').allTextContents(),forms:await page.locator('form').count(),labels:await page.locator('form label').allTextContents(),errors:await page.locator('.status-box.error').allTextContents()}));
 throw error;
}finally{await browser.close();}
