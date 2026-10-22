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
await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 await page.goto(origin+'/admin/prices');await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
 const form=page.locator('form.admin-form').first();
 await form.locator('[name=commodity_id]').selectOption({label:'Egusi'});await form.locator('[name=market_id]').selectOption({label:'Kwali Market'});
 await form.getByLabel('Low',{exact:true}).fill('100');await form.getByLabel('High',{exact:true}).fill('200');await form.getByLabel('Average',{exact:true}).fill('150');
 await form.getByLabel('Bag size (kg)',{exact:true}).fill('Unknown');await form.getByLabel('Update date/time',{exact:true}).fill(new Date().toISOString().slice(0,16));
 await form.locator('[name=confidence_level]').selectOption('Verified by 2 sources');
 async function submit(status){const wait=page.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');await form.getByRole('button',{name:'Create pending update',exact:true}).click();const r=await wait;assert.equal(r.status(),status);return r.json();}
 const missing=await submit(422);assert.ok(missing.detail.includes('two different references'));
 await form.getByRole('button',{name:/Show extra fields/}).click();await form.getByLabel('Source 1 (private)',{exact:true}).fill('SYNTHETIC-CLAIM-ONE');await form.getByLabel('Source 2 (private)',{exact:true}).fill('synthetic-claim-one');
 await submit(422);await form.getByLabel('Source 2 (private)',{exact:true}).fill('SYNTHETIC-CLAIM-TWO');
 await form.locator('[name=movement]').selectOption('up');const manual=await submit(201);assert.equal(manual.movement,'up');
 await form.locator('[name=movement]').selectOption('unknown');const saved=await submit(201);assert.equal(saved.movement,'unknown');assert.equal(saved.bag_size,'Unknown');
 const proof=await page.evaluate(async id=>{const session=await fetch('/api/auth/browser/session').then(r=>r.json());const headers={'X-PriceYard-CSRF':session.csrf_token,'X-PriceYard-Session':session.session_id};const approval=await fetch(`/api/price-updates/${id}/approve`,{method:'PATCH',headers});if(!approval.ok)throw Error('Synthetic approval failed');const pub=await(await fetch('/api/price-updates')).json();return pub.find(x=>x.id===id);},saved.id);
 assert.ok(proof);assert.equal(proof.confidence_level,'Verified by 2 sources');assert.equal('source_1' in proof,false);assert.equal('source_2' in proof,false);
 assert.equal(await page.getByLabel(/grade/i).count(),0);await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));assert.equal(outside,0);
 const report={original_admin_form:true,missing_or_duplicate_private_references_rejected:true,owner_restored_manual_admin_movement:true,explicit_unknown_saves_and_approves:true,private_evidence_excluded_from_public_response:true,no_grade_or_measurement_fields_added:true,mobile_layout_preserved:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/price-claim-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
