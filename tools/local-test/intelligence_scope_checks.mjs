import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0,createdCommodity;const created=[],captures=[],pending=[];
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(endpoint,method='GET',body){return page.evaluate(async({endpoint,method,body})=>{const response=await fetch('/api'+endpoint,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});return {status:response.status,body:response.status===204?null:await response.json()};},{endpoint,method,body});}
try {
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
  const originalPrices=(await api('/price-updates/admin/history')).body,commodities=(await api('/commodities')).body;
  const egusi=commodities.find(row=>row.name==='Egusi'),price=originalPrices.find(row=>row.commodity_id===egusi.id);
  let palm=commodities.find(row=>row.name==='Palm oil');
  if(!palm){const response=await api('/commodities','POST',{name:'Palm oil'});assert.equal(response.status,201);palm=response.body;createdCommodity=palm.id;}
  const marker='Synthetic scoped '+crypto.randomUUID();
  const cases=[
    ['market-signals',{signal_type:marker+' Egusi market',signal_description:'Synthetic scope observation'},{signal_type:marker+' Palm market',signal_description:'Synthetic unrelated observation'}],
    ['quality-signals',{quality_status:marker+' Egusi quality'},{quality_status:marker+' Palm quality'}],
    ['cost-breakdowns',{purchase_price_reference:210000,transport:120,warehouse:80},{purchase_price_reference:310000,transport:120,warehouse:80}],
  ];
  const before={};
  for(const [endpoint,own,other] of cases){
    before[endpoint]=(await api('/'+endpoint)).body;
    for(const [commodity,values] of [[egusi,own],[palm,other]]){
      const response=await api('/'+endpoint,'POST',{commodity_id:commodity.id,market_id:price.market_id,...values});assert.equal(response.status,201);created.push([endpoint,response.body.id]);
    }
    const all=(await api('/'+endpoint)).body;assert.ok(created.filter(row=>row[0]===endpoint).every(([,id])=>all.some(item=>item.id===id)),'Original unfiltered Admin list must retain both commodities');
  }
  const watch=new Set(cases.map(row=>'/api/'+row[0]));
  const listener=response=>{const url=new URL(response.url());if(watch.has(url.pathname)&&response.request().method()==='GET')pending.push(response.json().then(rows=>captures.push({endpoint:url.pathname,scope:url.searchParams.get('commodity_id'),rows,status:response.status()})));};
  page.on('response',listener);
  await page.goto(origin+'/commodities/Egusi');await page.getByText(marker+' Egusi market',{exact:true}).waitFor();await page.getByText(marker+' Egusi quality',{exact:true}).waitFor();
  await page.getByRole('heading',{name:'Cost breakdown',exact:true}).locator('..').getByText('Unit not recorded. Confirm the unit for this cost reference before using this estimate.',{exact:true}).waitFor();
  const calculator=page.getByRole('heading',{name:'Cost breakdown',exact:true}).locator('..').locator('.cost-calculator').first();
  assert.match(await calculator.innerText(),/210,200/);await calculator.getByRole('spinbutton').fill('2');assert.match(await calculator.innerText(),/420,400/);await calculator.getByRole('spinbutton').fill('1');
  await Promise.all(pending);page.off('response',listener);
  assert.equal(new Set(captures.map(row=>row.endpoint)).size,3);
  for(const capture of captures){assert.equal(capture.status,200);assert.equal(capture.scope,String(egusi.id));assert.ok(capture.rows.length>0&&capture.rows.every(row=>row.commodity_id===egusi.id));}
  assert.equal(await page.getByText(marker+' Palm market',{exact:true}).count(),0);assert.equal(await page.getByText(marker+' Palm quality',{exact:true}).count(),0);
  assert.doesNotMatch(await page.getByRole('heading',{name:'Cost breakdown',exact:true}).locator('..').innerText(),/310,000/);
  assert.deepEqual((await api('/price-updates/admin/history')).body,originalPrices);
  while(created.length){const [endpoint,id]=created.at(-1);assert.equal((await api('/'+endpoint+'/'+id,'DELETE')).status,204);created.pop();}
  for(const [endpoint] of cases)assert.deepEqual((await api('/'+endpoint)).body,before[endpoint]);
  if(createdCommodity){assert.equal((await api('/commodities/'+createdCommodity,'DELETE')).status,204);createdCommodity=undefined;}
  assert.deepEqual((await api('/commodities')).body,commodities);assert.equal(outside,0);
  const report={original_detail_sections_and_cost_formula_retained:true,three_intelligence_requests_filtered_on_server:true,original_unfiltered_admin_lists_retain_all_records:true,unrelated_rows_not_downloaded_or_displayed:true,historical_prices_unchanged:true,temporary_records_removed_and_catalog_restored:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/intelligence-scope-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {
  for(const [endpoint,id] of created.reverse())await api('/'+endpoint+'/'+id,'DELETE').catch(()=>{});
  if(createdCommodity)await api('/commodities/'+createdCommodity,'DELETE').catch(()=>{});
  await browser.close();
}
