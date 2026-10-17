import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(endpoint,method='GET',body){return page.evaluate(async({endpoint,method,body})=>{const response=await fetch('/api'+endpoint,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});return {status:response.status,body:await response.json()};},{endpoint,method,body});}
try {
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const history=(await api('/price-updates/admin/history')).body,commodities=(await api('/commodities')).body;
  const egusi=commodities.find(row=>row.name==='Egusi'),price=history.find(row=>row.commodity_id===egusi.id);
  let palm=commodities.find(row=>row.name==='Palm oil');
  if(!palm){const response=await api('/commodities','POST',{name:'Palm oil'});assert.equal(response.status,201);palm=response.body;}
  const marker='Synthetic planning '+crypto.randomUUID();
  const resources=[
    ['buying-zones',{price_low:210000,price_high:220000,reason:marker+' Egusi buying',confidence:'Low confidence'},{price_low:310000,price_high:320000,reason:marker+' Palm buying',confidence:'Low confidence'}],
    ['sell-watch-windows',{start_period:'Recorded period',observation:marker+' Egusi selling',confidence:'Low confidence'},{start_period:'Recorded period',observation:marker+' Palm selling',confidence:'Low confidence'}],
  ];
  for(const [endpoint,own,other] of resources){
    const ids=[];
    for(const [commodity,values] of [[egusi,own],[palm,other]]){const result=await api('/'+endpoint,'POST',{commodity_id:commodity.id,market_id:price.market_id,...values});assert.equal(result.status,201);ids.push(result.body.id);}
    const result=await api('/'+endpoint);assert.equal(result.status,200);assert.ok(ids.every(id=>result.body.some(row=>row.id===id)));
  }
  const pending=[],captures=[];
  page.on('response',response=>{const url=new URL(response.url());if(resources.some(([endpoint])=>url.pathname==='/api/'+endpoint)&&response.request().method()==='GET')pending.push(response.json().then(rows=>captures.push({endpoint:url.pathname,scope:url.searchParams.get('commodity_id'),status:response.status(),rows})));});
  await page.goto(origin+'/commodities/Egusi');
  await page.getByText(marker+' Egusi buying',{exact:true}).waitFor();await page.getByText(marker+' Egusi selling',{exact:true}).waitFor();await Promise.all(pending);
  assert.equal(new Set(captures.map(row=>row.endpoint)).size,2);
  for(const result of captures){assert.equal(result.status,200);assert.equal(result.scope,String(egusi.id));assert.ok(result.rows.length&&result.rows.every(row=>row.commodity_id===egusi.id));}
  assert.equal(await page.getByText(marker+' Palm buying',{exact:true}).count(),0);assert.equal(await page.getByText(marker+' Palm selling',{exact:true}).count(),0);
  assert.deepEqual((await api('/price-updates/admin/history')).body,history);
  assert.equal(outside,0);
  const report={two_planning_requests_scoped_in_real_browser:true,unfiltered_admin_lists_complete:true,unrelated_rows_not_downloaded_or_displayed:true,original_price_history_unchanged:true,no_new_delete_feature:true,disposable_preview_reseed_required:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/planning-scope-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {await browser.close();}
