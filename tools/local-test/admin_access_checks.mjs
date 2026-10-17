import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let outside=0;
async function fixture(email){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
 await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();
 return {context,page};
}
async function api(page,url){return page.evaluate(async url=>{
 const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
 const response=await fetch('/api'+url,{headers:{Authorization:'Bearer '+token}});
 return {status:response.status,body:await response.json()};
},url);}
try{
 const customer=await fixture('free'),admin=await fixture('admin');
 const before=await api(customer.page,'/auth/me');assert.equal(before.status,200);const id=before.body.id;
 const auditBefore=(await api(admin.page,'/audit-logs')).body.map(row=>row.id);
 await admin.page.goto(origin+'/admin/users');await admin.page.getByRole('heading',{name:'Users',exact:true}).waitFor();
 const row=admin.page.locator('.admin-table-view tbody tr').filter({hasText:'free@example.com'});
 async function userAction(action){
  const saved=admin.page.waitForResponse(r=>r.url()===origin+'/api/users/'+id&&r.request().method()==='PATCH');
  const reloaded=admin.page.waitForResponse(r=>r.url()===origin+'/api/users'&&r.request().method()==='GET');
  await action();assert.equal((await saved).status(),200);await (await reloaded).finished();
  await admin.page.locator('.status-box.success').getByText('User updated.',{exact:true}).waitFor();
  await row.waitFor();
 }
 await userAction(()=>row.getByRole('combobox').selectOption('paid_user'));
 let sub=(await api(customer.page,'/subscriptions/'+id)).body;assert.equal(sub.status,'active');assert.equal(sub.end_date,null);
 await userAction(()=>row.getByRole('button',{name:'Deactivate',exact:true}).click());
 assert.equal((await api(customer.page,'/auth/me')).status,403);
 await userAction(()=>row.getByRole('button',{name:'Activate',exact:true}).click());
 assert.equal((await api(customer.page,'/auth/me')).status,401);
 const fresh=await fixture('free');assert.equal((await api(fresh.page,'/auth/me')).status,200);
 await admin.page.goto(origin+'/admin/subscriptions');await admin.page.getByRole('heading',{name:'Subscriptions',exact:true}).waitFor();
 const subscriptionRow=admin.page.getByRole('cell',{name:'#'+id,exact:true}).locator('..');
 const saved=admin.page.waitForResponse(r=>r.url()===origin+'/api/subscriptions/'+id+'/status'&&r.request().method()==='PATCH');
 await subscriptionRow.getByRole('combobox').selectOption('free');assert.equal((await saved).status(),200);
 sub=(await api(fresh.page,'/subscriptions/'+id)).body;assert.equal(sub.status,'free');assert.equal(sub.end_date,null);
 assert.equal((await api(fresh.page,'/auth/me')).body.role,'free_user');
 const audits=(await api(admin.page,'/audit-logs')).body.filter(row=>!auditBefore.includes(row.id));
 assert.equal(audits.filter(row=>row.action==='user.update').length,3);
 assert.equal(audits.filter(row=>row.action==='subscription.user_management_sync').length,1);
 assert.equal(audits.filter(row=>row.action==='subscription.status_update').length,1);
 assert.equal(audits.filter(row=>row.action==='user.subscription_role_sync').length,1);
 assert.ok(!JSON.stringify(audits).includes('password_hash'));assert.equal(outside,0);
 const report={original_admin_role_and_status_controls:true,existing_indefinite_grant_rule_preserved:true,deactivation_denies_access:true,reactivation_rejects_old_token:true,original_password_still_works:true,original_subscription_control_restores_free_role:true,six_sanitized_audit_records:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/admin-access-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
