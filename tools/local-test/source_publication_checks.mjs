import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url,text=false){return page.evaluate(async({url,text})=>{const token=localStorage.getItem('priceyard_access_token');const r=await fetch('/api'+url,{headers:token?{Authorization:'Bearer '+token}:{}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return text?r.text():r.json();},{url,text});}
try{
 await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();const current=await api('/price-updates');
 assert.ok(current.every(row=>!('source_1' in row)&&!('source_2' in row)));assert.ok(!(await page.locator('main').innerText()).includes('LOCAL-PRIVATE-SOURCE'));
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const before=await api('/price-updates/admin/history'),audits=await api('/audit-logs');assert.ok(before.every(row=>row.source_1==='LOCAL-PRIVATE-SOURCE'));
 await page.goto(origin+'/admin/prices');await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
 const hint='Shown to users. Keep source names and contact details in the private source fields.';
 for(const [index,description] of [[0,'create-price-note-visibility'],[1,'correct-price-note-visibility']]){
  const form=page.locator('form.admin-form').nth(index);
  await form.getByRole('button',{name:/Show extra fields/}).click();await form.getByText(hint,{exact:true}).waitFor();
  assert.equal(await form.getByLabel('Notes',{exact:true}).getAttribute('aria-describedby'),description);
 }
 const create=page.locator('form.admin-form').first();await create.locator('[name=commodity_id]').selectOption({label:'Egusi'});await create.locator('[name=market_id]').selectOption({label:'Kwali Market'});
 await create.getByRole('button',{name:'Prefill from last entry',exact:true}).click();await page.waitForFunction(()=>document.querySelector('form.admin-form [name=source_1]').value==='LOCAL-PRIVATE-SOURCE');assert.equal(await create.getByLabel('Source 1 (private)',{exact:true}).inputValue(),'LOCAL-PRIVATE-SOURCE');
 assert.equal(await page.getByLabel(/grade/i).count(),0);
 await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 assert.deepEqual(await api('/price-updates/admin/history'),before);assert.deepEqual(await api('/price-updates'),current);assert.deepEqual(await api('/audit-logs'),audits);
 assert.ok(!(await api('/reports/prices.csv',true)).includes('LOCAL-PRIVATE-SOURCE'));
 assert.ok(!(await api('/share/commodities/Egusi?commodity_id='+current[0].commodity_id,true)).includes('LOCAL-PRIVATE-SOURCE'));
 assert.equal(outside,0);
 const report={both_existing_notes_controls_labelled_public:true,accessible_hint_original_labels_preserved:true,legitimate_admin_source_prefill_preserved:true,public_prices_export_share_exclude_private_source:true,raw_source_history_public_notes_and_audits_unchanged:true,original_fields_and_mobile_layout:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/source-publication-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
