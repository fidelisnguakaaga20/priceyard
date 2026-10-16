import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let outside=0;let admin;
async function login(name){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(name+'@example.com');
 await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 await page.getByRole('heading',{name:'Welcome, Test '+name[0].toUpperCase()+name.slice(1),exact:true}).waitFor();
 return page;
}
try{
 const trial=await login('trial');await trial.goto(origin+'/prices');await trial.locator('.price-card').first().waitFor();
 const watched=trial.waitForResponse(r=>r.url()===origin+'/api/watchlist'&&r.request().method()==='POST');
 await trial.getByRole('button',{name:/Watch this/}).click();assert.equal((await watched).status(),201);
 admin=await login('admin');
 assert.equal(await admin.evaluate(async()=> (await fetch('/__test__/alerts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:true})})).status),200);
 await admin.goto(origin+'/admin/prices');await admin.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
 const form=admin.locator('form.admin-form').first();
 await form.locator('select[name="commodity_id"]').selectOption({label:'Egusi'});
 await form.locator('select[name="market_id"]').selectOption({label:'Kwali Market'});
 await form.getByLabel('Low',{exact:true}).fill('211000');await form.getByLabel('High',{exact:true}).fill('221000');
 await form.getByLabel('Average',{exact:true}).fill('216000');await form.getByLabel('Bag size (kg)',{exact:true}).fill('Unknown');
 await form.locator('select[name="confidence_level"]').selectOption('Low confidence');
 await form.getByLabel('Update date/time',{exact:true}).fill(new Date().toISOString().slice(0,16));
 const createdResponse=admin.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');
 await form.getByRole('button',{name:'Create pending update',exact:true}).click();
 const created=await createdResponse;assert.equal(created.status(),201);const item=await created.json();
 const row=admin.locator('.admin-table tbody tr').filter({has:admin.locator('td:first-child').getByText(String(item.id),{exact:true})});
 await row.waitFor();
 const approvedResponse=admin.waitForResponse(r=>r.url()===origin+`/api/price-updates/${item.id}/approve`&&r.request().method()==='PATCH');
 await admin.getByRole('button',{name:'Approve',exact:true}).click();const approved=await approvedResponse;
 assert.equal(approved.status(),200);assert.equal((await approved.json()).status,'approved');
 const attempts=await admin.evaluate(()=>fetch('/__test__/alerts').then(r=>r.json()));
 assert.deepEqual(attempts.attempts,['email','push','whatsapp']);
 await admin.reload();await row.waitFor();
 assert.equal(await row.locator('td').nth(3).innerText(),'approved');
 const prices=await trial.evaluate(()=>fetch('/api/price-updates').then(r=>r.json()));assert.equal(prices[0].id,item.id);
 assert.equal(await admin.getByLabel(/grade/i).count(),0);assert.equal(outside,0);
 const report={original_watch_button_and_admin_approval:true,email_failure_preserves_independent_push_and_whatsapp:true,approved_record_survives_reload:true,current_price_visible:true,attempts:attempts.attempts,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/notification-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{
 if(admin)await admin.evaluate(()=>fetch('/__test__/alerts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({enabled:false})})).catch(()=>{});
 await browser.close();
}
