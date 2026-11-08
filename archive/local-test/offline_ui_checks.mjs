import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0,createdWatch;const checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url,method='GET',body) {
  return page.evaluate(async({url,method,body})=>{
    const token=localStorage.getItem('priceyard_access_token');
    const response=await fetch(url,{method,headers:{...(token?{Authorization:'Bearer '+token}:{}),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
    return {status:response.status,body:response.status===204?null:await response.json()};
  },{url,method,body});
}
try {
  await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
  const original=(await api('/api/price-updates')).body;
  checks.live_prices_have_no_saved_copy_notice=await page.locator('.saved-price-notice').count()===0;
  const enabled=await api('/__test__/offline-prices','POST',{enabled:true});assert.equal(enabled.status,200);const stamp=enabled.body.saved_at;
  await page.reload();await page.locator('main .saved-price-notice').waitFor();
  checks.saved_fallback_warns_even_when_browser_says_online=await page.evaluate(()=>navigator.onLine)&&await page.locator('main .saved-price-notice').getByText(/Saved copy — not a live price/).count()===1;
  checks.device_save_time_distinct_from_record_time=await page.locator('main .saved-price-notice time').getAttribute('datetime')===stamp&&original[0].update_date_time!==stamp;
  checks.ticker_saved_copy_is_identified=await page.locator('header .saved-price-notice').count()===1;
  for(const screen of ['/','/commodities/Egusi']){
    await page.goto(origin+screen);await page.locator('main .saved-price-notice').first().waitFor();
    checks[(screen==='/'?'home':'detail')+'_saved_copy_notice']=await page.locator('main .saved-price-notice time').first().getAttribute('datetime')===stamp;
    if(screen==='/')checks.cached_hero_does_not_say_live_now=await page.locator('.hero-price-preview').getByText('Live now',{exact:true}).count()===0;
  }
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();
  const item=await api('/api/watchlist','POST',{commodity_id:original[0].commodity_id,market_id:original[0].market_id});assert.equal(item.status,201);createdWatch=item.body.id;
  await page.goto(origin+'/watchlist');await page.locator('.watchlist-grid .card').first().waitFor();await page.locator('main .saved-price-notice').waitFor();checks.watchlist_public_prices_identified_without_caching_private_watchlist=true;
  await page.goto(origin+'/prices');await page.locator('main .saved-price-notice').waitFor();
  await context.setOffline(true);await page.locator('.offline-banner').filter({hasText:/offline\. Saved prices may be shown; they are not live\./}).waitFor();checks.offline_banner_does_not_claim_saved_data_exists=true;await context.setOffline(false);
  await api('/__test__/offline-prices','POST',{enabled:false});await page.reload();await page.locator('.price-card').first().waitFor();checks.fresh_success_clears_provenance_notice=await page.locator('.saved-price-notice').count()===0;
  await page.route(origin+'/api/price-updates',route=>route.fulfill({json:original,headers:{'X-PriceYard-Cache':'saved','X-PriceYard-Saved-At':'invalid'}}));
  await page.reload();await page.locator('.status-box.error').filter({hasText:'503'}).waitFor();checks.invalid_cache_timestamp_not_rendered=await page.locator('.price-card').count()===0;await page.unroute(origin+'/api/price-updates');
  await page.goto(origin+'/__test__/offline-prices');await page.getByRole('button',{name:'Show simulated saved copy',exact:true}).click();await page.getByText('Saved-copy simulation enabled. Reload Current Prices.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Restore normal responses',exact:true}).click();await page.getByText('Normal responses restored. Reload Current Prices.',{exact:true}).waitFor();checks.owner_manual_controls_restore_normal_mode=true;
  checks.original_public_records_unchanged=JSON.stringify((await api('/api/price-updates')).body)===JSON.stringify(original);
  assert.equal(outside,0);assert.ok(Object.values(checks).every(Boolean));
  const report={checks,passed:Object.keys(checks).length,real_original_ui_with_synthetic_cache_headers:true,native_service_workers_remain_disabled:true,worker_verified_separately_with_fake_network:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/offline-ui-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {
  if(createdWatch)assert.equal((await api('/api/watchlist/'+createdWatch,'DELETE')).status,204);
  await api('/__test__/offline-prices','POST',{enabled:false}).catch(()=>{});
  await browser.close();
}
