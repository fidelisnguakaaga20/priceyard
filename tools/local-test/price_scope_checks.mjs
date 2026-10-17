import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
let outside=0,targetId;
const created=[];
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
async function api(url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)})});
 return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method,body});}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const history=(await api('/price-updates/admin/history')).body;
 const price=history.find(row=>row.status==='approved');assert.ok(price);
 const target=await api('/commodities','POST',{name:'Synthetic scope target'});assert.equal(target.status,201);targetId=target.body.id;
 const checks={};
 for(const [endpoint,fields] of [['market-signals',{signal_type:'Synthetic',signal_description:'Synthetic saved observation'}],['quality-signals',{quality_status:'Synthetic saved observation'}],['storage-suitability',{suitability_status:'good'}]]){
  const payload={commodity_id:price.commodity_id,market_id:price.market_id,price_update_id:price.id,...fields};
  const saved=await api('/'+endpoint,'POST',payload);assert.equal(saved.status,201);created.push([endpoint,saved.body.id]);
  const audit=(await api('/audit-logs')).body;
  const denied=await api('/price-updates/'+price.id,'PATCH',{commodity_id:targetId});assert.equal(denied.status,409);
  assert.match(denied.body.detail,/linked records/);assert.ok(!JSON.stringify(denied.body).includes('PRIVATE'));
  assert.deepEqual((await api('/price-updates/admin/history')).body,history);
  assert.deepEqual((await api('/'+endpoint+'/'+saved.body.id)).body,saved.body);
  const invalid=await api('/'+endpoint,'POST',{...payload,commodity_id:targetId});assert.equal(invalid.status,422);
  assert.deepEqual((await api('/audit-logs')).body,audit);
  checks[endpoint+'_linked_scope_and_saved_data_preserved']=true;
 }
 await page.goto(origin+'/admin/prices');await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
 assert.ok((await page.locator('.admin-table').innerText()).includes('Egusi'));
 assert.equal(await page.getByRole('button',{name:'Save correction',exact:true}).count(),1);
 assert.equal(outside,0);
 const report={checks,original_price_history_unchanged:true,original_admin_price_screen:true,no_new_measurement_or_form_fields:true,disposable_preview_reseed_required:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/price-scope-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{
 for(const [endpoint,id] of created.reverse())if(endpoint!=='storage-suitability')await api('/'+endpoint+'/'+id,'DELETE').catch(()=>{});
 if(targetId)await api('/commodities/'+targetId,'DELETE').catch(()=>{});
 await browser.close();
}
