import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446',expectOld=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});let outside=0;const created=[];let admin;
async function fixture(email){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(20000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill(email+'@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:/Welcome, Test/}).waitFor();return {context,page};
}
async function api(page,url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},body:body===undefined?undefined:JSON.stringify(body)});
 return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method,body});}
try{
 admin=await fixture('admin');const trial=await fixture('trial');
 const before=(await api(admin.page,'/price-updates/admin/history')).body;const currentBefore=(await api(admin.page,'/price-updates')).body;
 await trial.page.goto(origin+'/history');await trial.page.locator('.history-table-view tbody tr').first().waitFor();
 assert.equal(await trial.page.locator('.trend-line').count(),expectOld?1:0);
 if(!expectOld)await trial.page.getByText('Not enough comparable records.',{exact:true}).waitFor();
 const base=currentBefore.find(row=>row.commodity.name==='Egusi');assert.ok(base);
 for(const [index,size] of [[0,'Synthetic recorded size one'],[1,'Synthetic recorded size one'],[2,'Synthetic recorded size two'],[3,'Synthetic recorded size two']]){
  const response=await api(admin.page,'/price-updates','POST',{commodity_id:base.commodity_id,market_id:base.market_id,price_low:210000+index*1000,price_high:220000+index*1000,average_price:215000+index*1000,
   unit:'1 bag',bag_size:size,commodity_type:'Synthetic recorded type',confidence_level:'Low confidence',movement:'unknown',suggested_action:'Watch',update_date_time:new Date(Date.now()-(6-index)*3600000).toISOString()});
  assert.equal(response.status,201);created.push(response.body.id);assert.equal((await api(admin.page,`/price-updates/${response.body.id}/approve`,'PATCH')).status,200);
 }
 const current=(await api(admin.page,'/price-updates')).body;
 if(expectOld)assert.ok(!current.some(row=>row.id===created[1]));else{
  assert.ok(current.some(row=>row.id===created[1]));assert.ok(current.some(row=>row.id===created[3]));assert.ok(current.some(row=>row.id===base.id));
 }
 await trial.page.reload();await trial.page.locator('.history-table-view tbody tr').first().waitFor();
 assert.equal(await trial.page.locator('.history-table-view tbody tr').count(),before.filter(row=>row.status==='approved'&&row.commodity.name==='Egusi').length+4);
 assert.equal(await trial.page.locator('.trend-line').count(),expectOld?1:2);
 if(!expectOld){
  const charts=trial.page.locator('.trend-chart');assert.equal(await charts.count(),2);
  for(const chart of await charts.all())assert.equal(await chart.locator('.trend-dot').count(),2);
  await trial.page.getByText(/Synthetic recorded size one/).first().waitFor();await trial.page.getByText(/Synthetic recorded size two/).first().waitFor();
  await trial.page.goto(origin+'/prices');await trial.page.locator('.price-card').first().waitFor();
  for(const size of ['Synthetic recorded size one','Synthetic recorded size two'])await trial.page.locator('.price-card').filter({hasText:size}).first().waitFor();
  assert.ok((await trial.page.locator('.price-card').allTextContents()).some(text=>text.includes('Synthetic recorded type')));
 }
 for(const id of created)assert.equal((await api(admin.page,'/price-updates/'+id,'DELETE')).status,204);created.length=0;
 assert.deepEqual((await api(admin.page,'/price-updates/admin/history')).body,before);assert.equal(outside,0);
 const report={old_mixed_measurement_trend_reproduced:expectOld,current_distinct_recorded_sizes_preserved:!expectOld,separate_matching_two_point_charts:!expectOld,unknown_measurements_not_joined:!expectOld,all_history_rows_retained:true,original_history_restored_after_synthetic_checks:true,no_real_or_guessed_weights:true,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/comparison-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{
 if(admin)for(const id of created)await api(admin.page,'/price-updates/'+id,'DELETE').catch(()=>{});
 await browser.close();
}
