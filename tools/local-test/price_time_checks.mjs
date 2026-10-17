import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectOld=process.argv.includes('--expect-bug');let outside=0;const cases=[];
async function fixture(email,timezoneId){
 const context=await browser.newContext({timezoneId,extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
 return {context,page};
}
function check(response,sent,local,iso,old){
 assert.equal(sent.update_date_time,old?local:iso);
 assert.equal(response.update_date_time,old?local+':00':iso.replace('.000Z','Z'));
 assert.equal(response.unit,'1 bag');assert.equal(response.bag_size,'Unknown');assert.equal(response.status,'pending');
 assert.ok(!Object.keys(response).some(key=>/grade/i.test(key)));
}
try{
 for(const timezoneId of ['Africa/Lagos','UTC']){
  const {context,page}=await fixture('admin',timezoneId);await page.goto(origin+'/admin/prices');await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
  const create=page.locator('form.admin-form').nth(0);
  await create.locator('select[name="commodity_id"]').selectOption({label:'Egusi'});await create.locator('select[name="market_id"]').selectOption({label:'Kwali Market'});
  for(const [label,value] of [['Low','211000'],['High','221000'],['Average','216000'],['Bag size (kg)','Unknown'],['Update date/time','2026-10-16T15:30']])await create.getByLabel(label,{exact:true}).fill(value);
  const created=page.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');
  await create.getByRole('button',{name:'Create pending update',exact:true}).click();const response=await created;assert.equal(response.status(),201);const record=await response.json();
  const iso=timezoneId==='Africa/Lagos'?'2026-10-16T14:30:00.000Z':'2026-10-16T15:30:00.000Z';
  check(record,response.request().postDataJSON(),'2026-10-16T15:30',iso,expectOld);
  const edit=page.locator('form.admin-form').nth(1);await edit.getByLabel('Update date/time',{exact:true}).fill('2026-10-16T16:45');
  const corrected=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/'+record.id&&r.request().method()==='PATCH');
  await edit.getByRole('button',{name:'Save correction',exact:true}).click();const correction=await corrected;assert.equal(correction.status(),200);
  const correctedIso=timezoneId==='Africa/Lagos'?'2026-10-16T15:45:00.000Z':'2026-10-16T16:45:00.000Z';
  check(await correction.json(),correction.request().postDataJSON(),'2026-10-16T16:45',correctedIso,expectOld);
  await page.reload();await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
  const saved=await page.evaluate(async id=>{
   const token=localStorage.getItem('priceyard_access_token');const rows=await fetch('/api/price-updates/admin/history',{headers:{Authorization:'Bearer '+token}}).then(r=>r.json());return rows.find(row=>row.id===id);
  },record.id);
  // SQLite preserves the UTC wall time but omits its offset; PostgreSQL's aware
  // round trip is separately verified. No browser-local reinterpretation here.
  assert.equal(saved.update_date_time,(expectOld?'2026-10-16T16:45:00':correctedIso.replace('.000Z','')));
  cases.push({timezone:timezoneId,admin_create_and_correction:true,saved_after_reload:true,utc_conversion:!expectOld});await context.close();
 }
 const {context,page}=await fixture('reporter','Africa/Lagos');await page.goto(origin+'/report-price');
 await page.getByRole('heading',{name:'Report a market price',exact:true}).waitFor();const form=page.locator('form');
 await form.locator('select[name="commodity_id"]').selectOption({label:'Egusi'});await form.locator('select[name="market_id"]').selectOption({label:'Kwali Market'});
 for(const [name,value] of [['price_low','211000'],['price_high','221000'],['bag_size','Unknown'],['update_date_time','2026-10-16T15:30']])await form.locator('[name="'+name+'"]').fill(value);
 const reported=page.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');await form.getByRole('button',{name:'Submit price report',exact:true}).click();
 const response=await reported;assert.equal(response.status(),201);check(await response.json(),response.request().postDataJSON(),'2026-10-16T15:30','2026-10-16T14:30:00.000Z',false);
 await context.close();assert.equal(outside,0);
 const report={admin_original_naive_timestamp_reproduced:expectOld,cases,existing_reporter_utc_behavior_preserved:true,original_forms_measurements_and_status_preserved:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/price-time-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
