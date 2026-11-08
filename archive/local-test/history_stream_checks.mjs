import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
try{
 await page.goto(origin+'/__test__/status');
 const before=await page.evaluate(()=>fetch('/api/price-updates',{credentials:'omit'}).then(r=>r.json()));
 const fixture=await page.evaluate(()=>fetch('/__test__/history-stream',{method:'POST'}).then(r=>r.json()));assert.equal(fixture.synthetic_only,true);assert.equal(fixture.ids.length,251);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();
 const incoming=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/price-updates/history');await page.goto(origin+'/history');const response=await incoming;assert.equal(response.status(),200);assert.ok(response.headers()['cache-control'].includes('no-store'));assert.equal(response.headers()['content-length'],undefined);
 const rows=await response.json();assert.deepEqual(rows.map(row=>row.id),fixture.ids);assert.ok(rows.every(row=>row.bag_size===null&&row.commodity_type===null&&!('source_1' in row)&&!('source_2' in row)));
 await page.waitForFunction(()=>document.querySelectorAll('.history-table-view tbody tr').length===251);assert.equal(await page.locator('.history-card-list article').count(),251);
 await page.locator('.filter-bar select').nth(1).selectOption('id:'+fixture.market_id);await page.locator('.filter-bar select').nth(2).selectOption('morning');
 const filtered=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/price-updates/history'&&new URL(r.url()).searchParams.get('time_of_day')==='morning');await page.getByRole('button',{name:'Search history',exact:true}).click();assert.deepEqual((await(await filtered).json()).map(row=>row.id),fixture.morning_ids);
 await page.waitForFunction(count=>document.querySelectorAll('.history-table-view tbody tr').length===count,fixture.morning_ids.length);
 await page.locator('.filter-bar select').nth(2).selectOption('');const full=page.waitForResponse(r=>new URL(r.url()).pathname==='/api/price-updates/history'&&!new URL(r.url()).searchParams.has('time_of_day'));await page.getByRole('button',{name:'Search history',exact:true}).click();assert.equal((await(await full).json()).length,251);
 await page.setViewportSize({width:375,height:812});await page.waitForFunction(()=>document.querySelectorAll('.history-card-list article').length===251);assert.equal(await page.locator('.history-card-list article').last().isVisible(),true);assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1));
 assert.equal(await page.getByText(/Grade:|Grade not recorded/).count(),0);const after=await page.evaluate(()=>fetch('/api/price-updates',{credentials:'omit'}).then(r=>r.json()));assert.deepEqual(after,before);
 assert.equal(outside,0);const report={complete_history_records:251,original_desktop_rows_and_mobile_cards:251,original_market_and_time_filters:true,chronological_order_with_ties:true,unknown_measurements_preserved:true,current_prices_unchanged:true,source_privacy_and_no_store:true,no_history_or_chart_truncation:true,external_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/history-stream-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
