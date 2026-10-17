import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const created=[],checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(10000);
async function api(endpoint,method='GET',body){return page.evaluate(async({endpoint,method,body})=>{
  const response=await fetch('/api'+endpoint,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  return {status:response.status,body:response.status===204?null:await response.json()};
},{endpoint,method,body});}
try{
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const history=(await api('/price-updates/admin/history')).body,price=history[0],original=(await api('/cost-breakdowns')).body;
  await page.goto(origin+'/admin/costs');const form=page.locator('form.admin-form');
  for(const [name,value] of Object.entries({commodity_id:price.commodity_id,market_id:price.market_id,transport:'999999999999.99',warehouse:'0.01',purchase_price_reference:0}))await form.locator('[name='+name+']').fill(String(value));
  let response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/cost-breakdowns');
  await form.getByRole('button',{name:'Save cost breakdown',exact:true}).click();assert.equal((await response).status(),422);
  await page.locator('.status-box.error').filter({hasText:'Calculated cost total exceeds the existing storage limit'}).waitFor();
  checks.invalid_total_uses_existing_form_error=true;
  checks.rejected_creation_does_not_change_records=JSON.stringify((await api('/cost-breakdowns')).body)===JSON.stringify(original);
  for(const [name,value] of Object.entries({transport:'120.50',warehouse:'80.25',purchase_price_reference:210000}))await form.locator('[name='+name+']').fill(String(value));
  response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/cost-breakdowns');await form.getByRole('button',{name:'Save cost breakdown',exact:true}).click();const added=await response;assert.equal(added.status(),201);const saved=await added.json();created.push(saved.id);
  checks.original_cost_calculation_preserved=Number(saved.total_additional_cost)===200.75&&Number(saved.total_estimated_landing_storage_cost)===210200.75;
  const id=form.locator('[name=id]');await id.fill(String(saved.id));await page.waitForFunction(()=>document.querySelector('form [name=id]').validationMessage==='');
  const audits=(await api('/audit-logs')).body,stored=(await api('/cost-breakdowns/'+saved.id)).body;
  await form.locator('[name=transport]').fill('999999999999.99');
  response=page.waitForResponse(r=>r.request().method()==='PATCH'&&new URL(r.url()).pathname==='/api/cost-breakdowns/'+saved.id);await form.getByRole('button',{name:'Save cost breakdown',exact:true}).click();assert.equal((await response).status(),422);
  checks.rejected_edit_preserves_saved_details_and_audits=JSON.stringify((await api('/cost-breakdowns/'+saved.id)).body)===JSON.stringify(stored)&&JSON.stringify((await api('/audit-logs')).body)===JSON.stringify(audits);
  checks.null_cost_is_validation_error=(await api('/cost-breakdowns/'+saved.id,'PATCH',{transport:null})).status===422;
  await form.locator('[name=transport]').fill('');
  response=page.waitForResponse(r=>r.request().method()==='PATCH'&&new URL(r.url()).pathname==='/api/cost-breakdowns/'+saved.id);await form.getByRole('button',{name:'Save cost breakdown',exact:true}).click();assert.equal((await response).status(),200);
  await page.reload();await id.fill(String(saved.id));await page.waitForFunction(()=>document.querySelector('form [name=id]').validationMessage==='');
  checks.original_explicit_zero_and_prefill_reload_preserved=Number(await form.locator('[name=transport]').inputValue())===0&&Number(await form.locator('[name=warehouse]').inputValue())===80.25;
  assert.equal((await api('/cost-breakdowns/'+saved.id,'DELETE')).status,204);
  checks.original_prices_and_costs_unchanged=JSON.stringify((await api('/price-updates/admin/history')).body)===JSON.stringify(history)&&JSON.stringify((await api('/cost-breakdowns')).body)===JSON.stringify(original);
  assert.equal(outside,0);const failures=Object.entries(checks).filter(([,ok])=>!ok).map(([key])=>key);
  const report={checks,failures,external_page_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/cost-validation-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));assert.deepEqual(failures,[]);
}finally{for(const id of created)await api('/cost-breakdowns/'+id,'DELETE').catch(()=>{});await browser.close();}
