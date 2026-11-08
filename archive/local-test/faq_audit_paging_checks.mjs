import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url){return page.evaluate(async url=>{const r=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return r.json();},url);}
async function cards(count){await page.waitForFunction(n=>document.querySelectorAll('.admin-card-list > article').length===n,count);}
async function faqAction(id,label,kind){
 await page.getByLabel('FAQ ID',{exact:true}).fill(String(id));
 const completion=page.waitForResponse(r=>r.url()===origin+'/api/faq/'+id+(kind==='delete'?'':'/'+kind)&&r.request().method()===(kind==='delete'?'DELETE':'PATCH'));
 await page.getByRole('button',{name:label,exact:true}).click();assert.equal((await completion).status(),kind==='delete'?204:200);
 await page.getByRole('button',{name:label,exact:true}).waitFor();await page.waitForFunction(()=>!document.querySelector('button:disabled:not(nav button)'));
}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const original={faq:await api('/faq'),prices:await api('/price-updates/admin/history')};
 await page.goto(origin+'/__test__/faq-audit-paging');await page.getByRole('button',{name:'Load synthetic FAQ and audit sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic FAQs and audit entries ready.',{exact:true}).waitFor();
 const audit=await api('/audit-logs');assert.equal(audit.length,205);assert.ok(!JSON.stringify(audit).includes('PRIVATE-PAGING'));
 const auditIds=[];
 for(const offset of [0,100,200]){
  const data=await api('/audit-logs/page?offset='+offset);assert.equal(data.total,205);assert.ok(data.items.length<=100);auditIds.push(...data.items.map(row=>row.id));
  await page.goto(origin+'/admin/audit'+(offset?'?offset='+offset:''));await page.waitForFunction(n=>document.querySelectorAll('.admin-table tbody tr').length===n,data.items.length);
  assert.ok(!(await page.locator('.admin-table').innerText()).includes('PRIVATE-PAGING'));
 }
 assert.deepEqual(auditIds,audit.map(row=>row.id));
 await page.reload();await page.waitForFunction(()=>document.querySelectorAll('.admin-table tbody tr').length===5);
 await page.getByRole('button',{name:'Previous',exact:true}).click();await page.waitForURL('**offset=100');await page.waitForFunction(()=>document.querySelectorAll('.admin-table tbody tr').length===100);
 checks.audit_all_ids_reachable_redaction_and_reload=true;
 const legacy=await api('/faq/admin');assert.equal(legacy.length,205);
 const expected=[...legacy].sort((a,b)=>Number(b.is_published)-Number(a.is_published)||a.category.localeCompare(b.category)||a.id-b.id);const ids=[];
 for(const offset of [0,100,200]){
  const data=await api('/faq/admin/page?offset='+offset);assert.equal(data.total,205);ids.push(...data.items.map(row=>row.id));
  await page.goto(origin+'/admin/faq'+(offset?'?offset='+offset:''));await cards(data.items.length);
 }
 assert.deepEqual(ids,expected.map(row=>row.id));checks.faq_all_ids_reachable_original_publication_groups=true;
 const target=expected.at(-1);assert.equal(target.is_published,false);assert.ok(target.question.startsWith('ZZ synthetic FAQ'));
 await page.goto(origin+'/admin/faq?offset=100');await cards(100);await page.getByLabel('FAQ ID',{exact:true}).fill(String(target.id));
 const edit=page.locator('form.admin-form').nth(1);
 await edit.getByLabel('Question',{exact:true}).fill(target.question);await edit.getByLabel('Answer',{exact:true}).fill('Edited hidden paging answer');await edit.getByLabel('Category',{exact:true}).fill(target.category);
 const saved=page.waitForResponse(r=>r.url()===origin+'/api/faq/'+target.id&&r.request().method()==='PATCH');await edit.getByRole('button',{name:'Save FAQ',exact:true}).click();assert.equal((await saved).status(),200);await cards(100);
 assert.equal(new URL(page.url()).searchParams.get('offset'),'100');assert.equal((await api('/faq/admin')).find(row=>row.id===target.id).answer,'Edited hidden paging answer');
 assert.deepEqual(await api('/faq'),original.faq);
 await faqAction(target.id,'Publish','publish');assert.ok((await api('/faq')).some(row=>row.id===target.id));
 await faqAction(target.id,'Hide','hide');assert.deepEqual(await api('/faq'),original.faq);
 checks.off_page_known_id_edit_publish_hide_preserve_page_and_public_rules=true;
 await page.goto(origin+'/admin/faq?offset=200');await cards(5);await page.reload();await cards(5);
 const tail=(await api('/faq/admin/page?offset=200')).items;
 for(let index=0;index<tail.length;index++){
  assert.ok(tail[index].question.startsWith('ZZ synthetic FAQ'));assert.equal(tail[index].is_published,false);
  await faqAction(tail[index].id,'Delete','delete');
  if(index<4)await cards(4-index);else{await page.waitForURL('**/admin/faq?offset=100');await cards(100);}
 }
 checks.deleting_only_disposable_hidden_tail_returns_to_existing_page=true;
 for(const pathname of ['/admin/faq?offset=100','/admin/audit?offset=100']){
  await page.setViewportSize({width:375,height:812});await page.goto(origin+pathname);await page.getByRole('button',{name:'Previous',exact:true}).waitFor();
  assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 }
 assert.deepEqual(await api('/faq'),original.faq);assert.deepEqual(await api('/price-updates/admin/history'),original.prices);
 checks.original_public_faq_prices_and_mobile_layout_preserved=true;assert.equal(outside,0);
 const report={checks,records_per_sample:205,page_size:100,private_audit_markers_hidden:true,external_requests:outside,production_connections:0,reseed_preview_after_check:true};
 fs.writeFileSync(path.join(lab,'runtime/faq-audit-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
