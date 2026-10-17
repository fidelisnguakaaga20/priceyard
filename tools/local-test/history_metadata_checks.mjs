import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectOld=process.argv.includes('--expect-bug');let outside=0;
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();
 const expected=await page.evaluate(async()=>{
  const token=localStorage.getItem('priceyard_access_token');const response=await fetch('/api/price-updates/history',{headers:{Authorization:'Bearer '+token}});if(!response.ok)throw Error('Synthetic baseline failed');const rows=await response.json();
  return {count:rows.filter(row=>row.commodity.name==='Egusi').length,markets:[...new Set(rows.filter(row=>row.commodity.name==='Egusi').map(row=>row.market.name))].sort()};
 });
 const requests=[];page.on('request',request=>{const url=new URL(request.url());if(url.pathname.startsWith('/api/price-updates/history'))requests.push(url.pathname+url.search);});
 const metadata=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/history'+(expectOld?'':'/pairs'));
 await page.goto(origin+'/history');await (await metadata).finished();await page.locator('.history-table-view tbody tr').first().waitFor();
 assert.equal(await page.locator('.history-table-view tbody tr').count(),expected.count);
 const options=(await page.locator('.filter-bar select').nth(1).locator('option').allTextContents()).filter(option=>option!=='Choose a market').sort();assert.deepEqual(options,expected.markets);
 assert.equal(requests.filter(url=>url==='/api/price-updates/history').length,expectOld?1:0);
 assert.equal(requests.filter(url=>url==='/api/price-updates/history/pairs').length,expectOld?0:1);
 assert.equal(requests.filter(url=>url==='/api/price-updates/history?commodity=Egusi').length,1);
 if(!expectOld){
  const body=await page.evaluate(async()=>fetch('/api/price-updates/history/pairs',{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}}).then(r=>r.json()));
  for(const pair of body){assert.deepEqual(Object.keys(pair).sort(),['commodity','market']);assert.deepEqual(Object.keys(pair.commodity),['name']);assert.deepEqual(Object.keys(pair.market),['name']);}
 }
 assert.equal(outside,0);
 const report={original_all_history_metadata_download:expectOld,unfiltered_history_downloads:expectOld?1:0,filtered_history_downloads:1,compact_pair_requests:expectOld?0:1,original_market_options_preserved:true,all_matching_history_rows_preserved:true,no_private_metadata_fields:!expectOld,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/history-metadata-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
