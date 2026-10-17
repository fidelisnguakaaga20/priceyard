import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});let outside=0;const pending=[];
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(20000);
async function api(url,method='GET'){return page.evaluate(async({url,method})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method});}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
 const price=(await api('/price-updates')).body[0],before=(await api('/price-updates/admin/history')).body;const mark='Synthetic resource '+crypto.randomUUID();
 const cases=[
  ['market-signals','market-signals','market_signals','market_signal',{signal_type:'Synthetic observation',signal_description:mark},{signal_description:mark+' corrected'}],
  ['quality-signals','quality-signals','quality_signals','quality_signal',{quality_status:mark,risk_note:'Synthetic initial note'},{risk_note:'Synthetic corrected note'}],
  ['costs','cost-breakdowns','cost_breakdowns','cost_breakdown',{purchase_price_reference:'210000',transport:'120',warehouse:'80'},{purchase_price_reference:'211000'}]
 ];
 for(const [screen,pathName,table,prefix,fields,changes] of cases){
  await page.goto(origin+'/admin/'+screen);const form=page.locator('form.admin-form');await form.waitFor();
  for(const [name,value] of Object.entries({commodity_id:String(price.commodity_id),market_id:String(price.market_id),...fields}))await form.locator('[name="'+name+'"]').fill(value);
  if(screen!=='costs')await form.locator('[name=price_update_id]').fill(String(price.id));
  const creation=page.waitForResponse(r=>r.url()===origin+'/api/'+pathName&&r.request().method()==='POST');const reloaded=page.waitForResponse(r=>r.url()===origin+'/api/'+pathName&&r.request().method()==='GET');
  await form.getByRole('button',{name:/^Save /}).click();const response=await creation;assert.equal(response.status(),201);const item=await response.json();pending.push([pathName,item.id]);await (await reloaded).finished();await page.waitForFunction(()=>!document.querySelector('button:disabled'));
  await form.locator('[name=id]').fill(String(item.id));for(const [name,value] of Object.entries(changes))await form.locator('[name="'+name+'"]').fill(value);
  const edited=page.waitForResponse(r=>r.url()===origin+`/api/${pathName}/${item.id}`&&r.request().method()==='PATCH');const editReload=page.waitForResponse(r=>r.url()===origin+'/api/'+pathName&&r.request().method()==='GET');
  await form.getByRole('button',{name:/^Save /}).click();assert.equal((await edited).status(),200);await (await editReload).finished();await page.waitForFunction(()=>!document.querySelector('button:disabled'));
  const card=screen==='costs'?page.locator('.admin-card-list article').filter({hasText:new RegExp('#'+item.id+' · Commodity')}):page.locator('.admin-card-list article').filter({has:page.getByRole('heading',{name:screen==='market-signals'?mark+' corrected':mark,exact:true})});
  await card.waitFor();page.once('dialog',dialog=>dialog.accept());const deleted=page.waitForResponse(r=>r.url()===origin+`/api/${pathName}/${item.id}`&&r.request().method()==='DELETE');await card.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await deleted).status(),204);await card.waitFor({state:'hidden'});pending.pop();
  const logs=(await api('/audit-logs')).body.filter(row=>row.table_name===table&&row.record_id===item.id).sort((a,b)=>a.id-b.id);assert.deepEqual(logs.map(row=>row.action),['create','edit','delete'].map(action=>prefix+'.'+action));
  for(let index=1;index<logs.length;index++)for(const key of Object.keys(logs[index].old_value)){
   const numeric=screen==='costs'&&['transport','warehouse','security','market_charges','loading_offloading','other_costs','purchase_price_reference','total_additional_cost','total_estimated_landing_storage_cost'].includes(key);
   assert.deepEqual(numeric?Number(logs[index].old_value[key]):logs[index].old_value[key],numeric?Number(logs[index-1].new_value[key]):logs[index-1].new_value[key]);
  }
 }
 assert.deepEqual((await api('/price-updates/admin/history')).body,before);assert.equal(outside,0);
 const report={original_market_quality_cost_create_edit_delete_controls:true,complete_nine_audit_records:true,price_history_unchanged:true,temporary_resource_rows_removed:true,external_page_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/intelligence-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{for(const [pathName,id] of pending)await api('/'+pathName+'/'+id,'DELETE').catch(()=>{});await browser.close();}
