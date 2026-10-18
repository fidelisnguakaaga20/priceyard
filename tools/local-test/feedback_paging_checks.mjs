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
const page=await context.newPage();page.setDefaultTimeout(15000);page.on('dialog',d=>d.accept());
async function api(url){return page.evaluate(async url=>{const r=await fetch('/api'+url,{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});if(!r.ok)throw Error('Synthetic read failed '+r.status);return r.json();},url);}
async function cards(count){await page.waitForFunction(n=>document.querySelectorAll('.admin-card-list > article').length===n,count);}
async function summary(){const data=await api('/feedback/summary');await page.waitForFunction(data=>{const values=[...document.querySelectorAll('.admin-metric strong')].map(x=>x.textContent);return values[0]===String(data.count)&&values[1]===data.average_rating.toFixed(2);},data);return data;}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 const prices=await api('/price-updates/admin/history');
 await page.goto(origin+'/__test__/feedback-paging');await page.getByRole('button',{name:'Load synthetic feedback sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic feedback entries ready.',{exact:true}).waitFor();
 const before=await api('/feedback'),ids=[];assert.equal(before.length,205);
 for(const offset of [0,100,200]){
  const data=await api('/feedback/admin/page?offset='+offset);assert.equal(data.total,205);ids.push(...data.items.map(x=>x.id));
  await page.goto(origin+'/admin/feedback'+(offset?'?offset='+offset:''));await cards(data.items.length);await summary();
  assert.equal(await page.locator('.feedback-screenshot-thumb').count(),data.items.length);
 }
 assert.deepEqual(ids,before.map(x=>x.id));checks.all_ids_full_totals_and_private_screenshots_reachable=true;
 await page.reload();await cards(5);await page.getByRole('button',{name:'Previous',exact:true}).click();await page.waitForURL('**offset=100');await cards(100);await page.goBack();await page.waitForURL('**offset=200');await cards(5);checks.reload_previous_and_browser_back=true;
 const originalSummary=await summary(),filter=page.locator('label.admin-inline-filter select');
 await filter.selectOption('1');await cards(1);assert.equal(new URL(page.url()).searchParams.has('offset'),false);assert.deepEqual(await summary(),originalSummary);
 await page.reload();await cards(1);assert.equal(await filter.inputValue(),'1');
 await filter.selectOption('2');await cards(0);assert.deepEqual(await summary(),originalSummary);
 await filter.selectOption('5');await cards(100);await page.getByRole('button',{name:'Next',exact:true}).click();await cards(100);await page.getByRole('button',{name:'Next',exact:true}).click();await cards(4);
 assert.equal(new URL(page.url()).searchParams.get('rating'),'5');assert.deepEqual(await summary(),originalSummary);checks.filter_resets_offset_persists_on_reload_and_preserves_global_summary=true;
 const tail=(await api('/feedback/admin/page?rating=5&offset=200')).items,record=tail.at(-1);
 const card=()=>page.locator('.admin-card-list > article').filter({has:page.locator('.eyebrow',{hasText:new RegExp('^#'+record.id+'\\b')})});
 await card().getByPlaceholder('Display name (e.g. Mvendaga N.)',{exact:true}).fill('Synthetic public display');
 const published=page.waitForResponse(r=>r.url()===origin+'/api/feedback/'+record.id+'/testimonial/publish'&&r.request().method()==='PATCH');await card().getByRole('button',{name:'Feature as public testimonial',exact:true}).click();assert.equal((await published).status(),200);await cards(4);await card().getByRole('button',{name:'Remove from testimonials',exact:true}).waitFor();
 let publicRows=await api('/testimonials');assert.ok(publicRows.some(x=>x.id===record.id));assert.ok(!JSON.stringify(publicRows).includes('PRIVATE-FEEDBACK-MARKER'));assert.ok(publicRows.every(x=>!('screenshot_data' in x)&&!('user_id' in x)));
 const hidden=page.waitForResponse(r=>r.url()===origin+'/api/feedback/'+record.id+'/testimonial/hide'&&r.request().method()==='PATCH');await card().getByRole('button',{name:'Remove from testimonials',exact:true}).click();assert.equal((await hidden).status(),200);await cards(4);await card().getByRole('button',{name:'Feature as public testimonial',exact:true}).waitFor();
 publicRows=await api('/testimonials');assert.ok(!publicRows.some(x=>x.id===record.id));
 const kept=await api('/feedback/'+record.id);assert.equal(kept.screenshot_data,record.screenshot_data);assert.equal(kept.missing_market_request,record.missing_market_request);assert.equal(kept.comment,record.comment);assert.equal(new URL(page.url()).searchParams.get('offset'),'200');checks.original_feature_hide_and_private_evidence_preserved=true;
 await page.setViewportSize({width:375,height:812});assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));await page.setViewportSize({width:1280,height:900});checks.original_mobile_layout=true;
 for(let index=0;index<tail.length;index++){
  const row=page.locator('.admin-card-list > article').filter({has:page.locator('.eyebrow',{hasText:new RegExp('^#'+tail[index].id+'\\b')})});
  const removed=page.waitForResponse(r=>r.url()===origin+'/api/feedback/'+tail[index].id&&r.request().method()==='DELETE');await row.getByRole('button',{name:'Delete',exact:true}).click();assert.equal((await removed).status(),204);
  if(index<3)await cards(3-index);else{await page.waitForURL('**offset=100');await cards(100);}
 }
 assert.equal(new URL(page.url()).searchParams.get('rating'),'5');const afterSummary=await summary();assert.equal(afterSummary.count,201);assert.equal((await api('/feedback/admin/page?rating=5&offset=100')).total,200);checks.delete_tail_recovers_page_filter_and_full_summary=true;
 assert.deepEqual(await api('/price-updates/admin/history'),prices);assert.equal(outside,0);
 const report={checks,records:205,page_size:100,existing_prices_unchanged:true,external_requests:outside,production_connections:0,reseed_preview_after_check:true};
 fs.writeFileSync(path.join(lab,'runtime/feedback-paging-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}catch(error){console.log(JSON.stringify({url:page.url(),checks,cards:await page.locator('.admin-card-list > article').count()}));throw error;}
finally{await browser.close();}
