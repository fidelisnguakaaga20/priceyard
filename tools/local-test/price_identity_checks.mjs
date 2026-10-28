import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let external=0,original;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();external++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
async function api(url,method='GET',body){return page.evaluate(async({url,method,body})=>{
 const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body===undefined?{}:{body:JSON.stringify(body)})});
 return {status:response.status,body:response.status===204?null:await response.json()};
},{url,method,body});}
const checks={};
async function applyFilters(pathname,commodity,market,button){
 await page.goto(origin+pathname);await page.locator('.filter-bar select').first().locator('option').filter({hasText:commodity.name}).first().waitFor({state:'attached'});
 await page.locator('.filter-bar select').nth(0).selectOption('id:'+commodity.id);
 await page.locator('.filter-bar select').nth(1).selectOption('id:'+market.id);
 const reply=page.waitForResponse(response=>{const url=new URL(response.url());return url.pathname==='/api/price-updates'+(pathname==='/history'?'/history':'')&&url.searchParams.get('commodity_id')===String(commodity.id)&&url.searchParams.get('market_id')===String(market.id);});
 await page.getByRole('button',{name:button,exact:true}).click();const response=await reply;assert.equal(response.status(),200);
 const rows=await response.json();assert.ok(rows.length);assert.ok(rows.every(row=>row.commodity_id===commodity.id&&row.market_id===market.id));
 await page.locator('.loading-spinner').waitFor({state:'hidden'});return rows;
}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 original=(await api('/commodities')).body.find(row=>row.name==='Egusi');const market=(await api('/markets')).body.find(row=>row.name==='Kwali Market');assert.ok(original&&market);
 const historical=(await api('/price-updates/admin/history')).body;
 const prefix=await api('/commodities','POST',{name:'Egusi synthetic %20'});assert.equal(prefix.status,201);
 const duplicateMarket=await api('/markets','POST',{name:market.name,state:market.state==='Benue'?'FCT':'Benue'});assert.equal(duplicateMarket.status,201);
 for(const [commodity_id,market_id] of [[prefix.body.id,market.id],[original.id,duplicateMarket.body.id],[prefix.body.id,duplicateMarket.body.id]]){
  const created=await api('/price-updates','POST',{commodity_id,market_id,unit:'1 bag',bag_size:'Unknown',price_low:311000,price_high:321000,average_price:316000,suggested_action:'Watch',confidence_level:'Low confidence',update_date_time:new Date(Date.now()-60000).toISOString()});
  assert.equal(created.status,201,JSON.stringify(created.body));assert.equal((await api('/price-updates/'+created.body.id+'/approve','PATCH')).status,200);
 }
 const current=await applyFilters('/prices',original,market,'Search prices');assert.equal(current.length,1);assert.equal(await page.locator('.card-grid > article').count(),1);
 checks.current_exact_ids_exclude_prefix_and_same_named_market=true;
 const href=await page.getByRole('link',{name:'Market insights',exact:true}).first().getAttribute('href');assert.equal(new URL(href,origin).searchParams.get('commodity_id'),String(original.id));
 const oldRows=await applyFilters('/history',original,market,'Search history');assert.equal(oldRows.length,historical.filter(row=>row.commodity_id===original.id&&row.market_id===market.id&&row.status==='approved').length);
 checks.history_exact_ids_preserve_all_matching_records=true;
 await applyFilters('/prices',original,duplicateMarket.body,'Search prices');checks.same_named_market_can_be_selected_by_existing_id=true;
 const renamed='Egusi renamed synthetic';assert.equal((await api('/commodities/'+original.id,'PATCH',{name:renamed})).status,200);
 await page.goto(origin+href);await page.getByRole('heading',{name:renamed,exact:true}).waitFor();
 const detail=(await api('/price-updates?commodity_id='+original.id)).body;assert.ok(detail.every(row=>row.commodity_id===original.id));await page.locator('.intelligence-grid > article').nth(5).waitFor();assert.equal(await page.locator('.detail-grid > article').count(),0);
 checks.pre_rename_link_retains_original_commodity_identity=true;
 assert.deepEqual((await api('/price-updates/admin/history')).body.filter(row=>historical.some(before=>before.id===row.id)).map(row=>({id:row.id,commodity_id:row.commodity_id,market_id:row.market_id,price_low:row.price_low,price_high:row.price_high})),historical.map(row=>({id:row.id,commodity_id:row.commodity_id,market_id:row.market_id,price_low:row.price_low,price_high:row.price_high})));
 checks.existing_price_rows_and_amounts_unchanged=true;
 await page.goto(origin+'/commodities/'+encodeURIComponent(prefix.body.name));await page.getByRole('heading',{name:prefix.body.name,exact:true}).waitFor();await page.locator('.detail-grid > article').first().waitFor();assert.equal(await page.locator('.detail-grid > article').count(),2);
 checks.literal_percent_name_not_decoded_twice=true;
 await page.goto(origin+'/prices?commodity_id='+prefix.body.id+'&market_id='+duplicateMarket.body.id);await page.locator('.card-grid > article').waitFor();assert.equal(await page.locator('.card-grid > article').count(),1);assert.equal(await page.locator('.filter-bar select').nth(0).inputValue(),'id:'+prefix.body.id);
 checks.id_bookmark_restores_existing_filter_dropdowns=true;
 assert.equal(external,0);
 const report={checks,original_labels_and_form_fields_preserved:true,synthetic_preview_reseed_required:true,external_requests:external,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/price-identity-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{
 if(original)await api('/commodities/'+original.id,'PATCH',{name:original.name}).catch(()=>{});
 await browser.close();
}
