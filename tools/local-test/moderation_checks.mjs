import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});let outside=0;
async function fixture(email){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(20000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();return {context,page};
}
async function api(page,url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
 return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method,body});}
try{
 const customer=await fixture('trial'),admin=await fixture('admin');
 const screenshot='data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=';
 const comment='Synthetic moderation '+crypto.randomUUID();
 const feedback=await api(customer.page,'/feedback','POST',{rating:4,comment,screenshot_data:screenshot});assert.equal(feedback.status,201);const id=feedback.body.id;
 await admin.page.goto(origin+'/admin/feedback');const card=admin.page.locator('.admin-card-list article').filter({has:admin.page.getByRole('heading',{name:comment,exact:true})});await card.waitFor();
 await card.getByPlaceholder('Display name (e.g. Mvendaga N.)',{exact:true}).fill('Synthetic customer');
 const published=admin.page.waitForResponse(r=>r.url()===origin+`/api/feedback/${id}/testimonial/publish`);
 await card.getByRole('button',{name:'Feature as public testimonial',exact:true}).click();assert.equal((await published).status(),200);
 await card.getByRole('button',{name:'Remove from testimonials',exact:true}).waitFor();
 const testimonials=(await api(customer.page,'/testimonials')).body;assert.ok(testimonials.some(row=>row.id===id));assert.ok(!JSON.stringify(testimonials).includes('screenshot_data'));
 const hidden=admin.page.waitForResponse(r=>r.url()===origin+`/api/feedback/${id}/testimonial/hide`);
 await card.getByRole('button',{name:'Remove from testimonials',exact:true}).click();assert.equal((await hidden).status(),200);
 await card.getByRole('button',{name:'Feature as public testimonial',exact:true}).waitFor();
 assert.equal((await api(admin.page,'/feedback/'+id)).body.screenshot_data,screenshot);
 assert.ok(!(await api(customer.page,'/testimonials')).body.some(row=>row.id===id));
 admin.page.once('dialog',dialog=>dialog.accept());const removed=admin.page.waitForResponse(r=>r.url()===origin+'/api/feedback/'+id&&r.request().method()==='DELETE');
 await card.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await removed).status(),204);await card.waitFor({state:'hidden'});
 const historyBefore=(await api(admin.page,'/price-updates/admin/history')).body;
 await admin.page.goto(origin+'/admin/prices');const form=admin.page.locator('form.admin-form').first();
 await form.locator('select[name=commodity_id]').selectOption({label:'Egusi'});await form.locator('select[name=market_id]').selectOption({label:'Kwali Market'});
 for(const [name,value] of [['price_low','210000'],['price_high','220000'],['average_price','215000'],['bag_size','Unknown'],['update_date_time','2026-10-17T09:00']])await form.locator('[name='+name+']').fill(value);
 const created=admin.page.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');await form.getByRole('button',{name:'Create pending update',exact:true}).click();const priceResponse=await created;assert.equal(priceResponse.status(),201);const price=await priceResponse.json();
 const approved=admin.page.waitForResponse(r=>r.url()===origin+`/api/price-updates/${price.id}/approve`);await admin.page.getByRole('button',{name:'Approve',exact:true}).click();assert.equal((await approved).status(),200);
 assert.equal((await api(customer.page,`/price-updates/${price.id}/flag`,'POST',{reason:'Synthetic review'})).status,204);
 await admin.page.goto(origin+'/admin/flagged');await admin.page.getByRole('heading',{name:'Flagged prices',exact:true}).waitFor();
 const reviewed=admin.page.waitForResponse(r=>r.url()===origin+`/api/price-updates/${price.id}/flags/resolve`);await admin.page.getByRole('button',{name:'Mark reviewed',exact:true}).click();assert.equal((await reviewed).status(),204);
 await admin.page.getByText(/No open flags/).waitFor();
 await admin.page.goto(origin+'/admin/prices');await admin.page.getByLabel('Record ID',{exact:true}).fill(String(price.id));
 const deleted=admin.page.waitForResponse(r=>r.url()===origin+'/api/price-updates/'+price.id&&r.request().method()==='DELETE');await admin.page.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await deleted).status(),204);
 const historyAfter=(await api(admin.page,'/price-updates/admin/history')).body;assert.deepEqual(historyAfter,historyBefore);
 const audits=(await api(admin.page,'/audit-logs')).body;
 const feedbackLogs=audits.filter(row=>row.table_name==='feedback'&&row.record_id===id).sort((a,b)=>a.id-b.id);assert.equal(feedbackLogs.length,3);assert.ok(!JSON.stringify(feedbackLogs).includes('screenshot_data'));
 const priceLogs=audits.filter(row=>row.table_name==='price_updates'&&row.record_id===price.id);assert.ok(priceLogs.some(row=>row.action==='price_update.flags_resolve'));assert.equal(priceLogs.find(row=>row.action==='price_update.delete').new_value,null);assert.equal(outside,0);
 const report={original_testimonial_publish_hide_delete_controls:true,private_image_preserved_until_deliberate_fake_record_delete:true,new_audits_omit_image:true,original_flag_review_and_price_delete_controls:true,preexisting_synthetic_history_unchanged:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/moderation-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
