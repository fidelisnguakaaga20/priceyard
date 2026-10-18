import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446',expectOld=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});let outside=0,id,admin;
async function fixture(email){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(20000);await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();return {context,page};
}
async function api(page,url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method,body});}
try{
 admin=await fixture('admin');const trial=await fixture('trial');const before=(await api(admin.page,'/cost-breakdowns')).body;
 const price=(await api(admin.page,'/price-updates')).body[0];const created=await api(admin.page,'/cost-breakdowns','POST',{commodity_id:price.commodity_id,market_id:price.market_id,purchase_price_reference:210000,transport:120,warehouse:80});assert.equal(created.status,201);id=created.body.id;
 // NUMERIC(14,2) reads may serialize 120 as "120.00". Verify all amounts,
 // then compare the persisted response exactly across browser calculator use.
 const persisted=(await api(admin.page,'/cost-breakdowns/'+id)).body;
 const money=['transport','warehouse','security','market_charges','loading_offloading','other_costs','total_additional_cost','purchase_price_reference','total_estimated_landing_storage_cost'];
 for(const [key,value] of Object.entries(created.body)){
  if(money.includes(key))assert.equal(Number(persisted[key]),Number(value));else assert.deepEqual(persisted[key],value);
 }
 await trial.page.goto(origin+'/commodities/'+encodeURIComponent(price.commodity.name));const calculator=trial.page.locator('.cost-calculator');await calculator.waitFor();
 if(expectOld)await calculator.getByText("Priced per 1 bag. Enter how many you're buying to see your total cost.",{exact:true}).waitFor();
 else{await calculator.getByText('Unit not recorded. Confirm the unit for this cost reference before using this estimate.',{exact:true}).waitFor();assert.ok(!(await calculator.innerText()).includes('Priced per 1 bag'));}
 await calculator.getByLabel('How many are you buying?',{exact:true}).fill('2');await calculator.locator('dd').filter({hasText:'420,400'}).waitFor();
 assert.ok((await calculator.innerText()).includes('420,000'));assert.ok((await calculator.innerText()).includes('400'));
 assert.deepEqual((await api(admin.page,'/cost-breakdowns/'+id)).body,persisted);
 assert.equal((await api(admin.page,'/cost-breakdowns/'+id,'DELETE')).status,204);id=null;
 assert.deepEqual((await api(admin.page,'/cost-breakdowns')).body,before);assert.equal(outside,0);
 const report={unsupported_unit_inference_reproduced:expectOld,approved_honest_label_and_confirmation:!expectOld,original_quantity_and_totals_preserved:true,original_reference_record_unmodified:true,initial_cost_records_restored:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/cost-unit-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{if(id&&admin)await api(admin.page,'/cost-breakdowns/'+id,'DELETE').catch(()=>{});await browser.close();}
