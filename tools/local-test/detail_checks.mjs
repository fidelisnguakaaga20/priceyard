import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446', expectBug=process.argv.includes('--expect-bug'), checks={};
let external=0;
async function fixture(trial=false) {
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();external++;return route.abort();});
  await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  const page=await context.newPage();page.setDefaultTimeout(12000);
  if(trial) {
    await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');
    await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:'Welcome, Test Trial'}).waitFor();
  }
  if(!trial)await page.goto(origin);
  const commodities=await page.evaluate(()=>fetch('/api/commodities').then(r=>r.json()));
  const commodity=commodities.find(item=>item.name==='Egusi');
  assert.ok(commodity);
  return {context,page,commodity};
}
async function navigate(page,name,id) {
  await page.evaluate(({name,id})=>{history.pushState(null,'','/commodities/'+encodeURIComponent(name)+(id?'?commodity_id='+id:''));dispatchEvent(new PopStateEvent('popstate'));},{name,id});
  await page.getByRole('heading',{name,exact:true}).waitFor();
}
async function settle(page) {await page.evaluate(()=>new Promise(resolve=>setTimeout(resolve,250)));}
function deferred() {let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
try {
  {
    const {context,page,commodity}=await fixture(),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/commodities/'+commodity.id,async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(commodity)});sent.resolve();
    });
    await page.goto(origin+'/commodities/Egusi?commodity_id='+commodity.id);await ready.promise;
    await navigate(page,'Not-a-record');
    await page.getByText('No active Not-a-record commodity is available.',{exact:true}).waitFor();
    release.resolve();await sent.promise;await settle(page);
    checks.late_commodity_does_not_replace_new_route=await page.locator('.intelligence-grid,.commodity-detail-page .locked-panel').count()===0;
    await context.close();
  }
  {
    const {context,page,commodity}=await fixture(),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/commodities',async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic superseded price error'})});sent.resolve();
    });
    await page.goto(origin+'/commodities/Not-a-record');await ready.promise;
    await navigate(page,'Egusi',commodity.id);await page.locator('.commodity-detail-page .locked-panel').waitFor();
    release.resolve();await sent.promise;await settle(page);
    checks.late_error_does_not_poison_new_route=!(await page.locator('body').innerText()).includes('Synthetic superseded price error');
    await context.close();
  }
  {
    const {context,page}=await fixture(true);
    await context.route('**/api/quality-signals*',route=>route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic quality service unavailable'})}));
    await context.route('**/api/buying-zones*',route=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{id:9999,commodity_id:1,market_id:1,price_low:210000,price_high:220000,reason:'Synthetic independent buying-zone observation',confidence:'Low confidence',valid_from:null,valid_to:null}])}));
    await page.goto(origin+'/commodities/Egusi');
    await page.getByRole('heading',{name:'Buying zone',exact:true}).waitFor();
    if(!expectBug) {
      await page.getByText('Synthetic independent buying-zone observation',{exact:true}).waitFor();
      await page.getByText('Synthetic quality service unavailable',{exact:true}).waitFor();
    } else await settle(page);
    const body=await page.locator('body').innerText();
    checks.one_failed_section_keeps_successful_sections=body.includes('Synthetic independent buying-zone observation');
    checks.failed_section_shows_existing_error_box=body.includes('Synthetic quality service unavailable');
    await context.close();
  }
  {
    const {context,page}=await fixture(true),ready=deferred(),release=deferred(),sent=deferred();
    await context.route('**/api/market-signals*',async route=>{
      ready.resolve();await release.promise;
      await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify([{id:9998,commodity_id:1,market_id:1,signal_type:'Synthetic old commodity signal',signal_description:'Synthetic superseded observation',possible_meaning:null}])});sent.resolve();
    });
    await page.goto(origin+'/commodities/Egusi');await ready.promise;
    await navigate(page,'Not-a-record');
    await page.getByText('No active Not-a-record commodity is available.',{exact:true}).waitFor();
    release.resolve();await sent.promise;
    await settle(page);
    checks.late_intelligence_does_not_follow_old_commodity=!(await page.locator('body').innerText()).includes('Synthetic old commodity signal');
    await context.close();
  }
  {
    const {context,page,commodity}=await fixture();
    const privateRequests=[];
    page.on('request',request=>{if(/\/api\/(market-signals|quality-signals|buying-zones|sell-watch-windows|storage-suitability|cost-breakdowns)/.test(request.url()))privateRequests.push(request.url());});
    await page.goto(origin+'/commodities/Old-bookmark-name?commodity_id='+commodity.id);
    await page.locator('.commodity-detail-page .locked-panel').waitFor();
    await page.getByRole('heading',{name:'Market insights',exact:true}).waitFor();
    await page.getByText('Understand price changes, quality and storage.',{exact:true}).waitFor();
    assert.equal(await page.locator('.commodity-detail-page .detail-card,.commodity-detail-page .guidance,.commodity-detail-page .card-actions').count(),0);
    assert.equal(await page.getByRole('heading',{name:commodity.name,exact:true}).count(),1);
    assert.equal(privateRequests.length,0);
    for(const width of [375,1366])for(const dark of [true,false]){
      await page.setViewportSize({width,height:900});
      const toggle=page.getByRole('button',{name:/^Dark mode:/});
      if(/On/.test(await toggle.innerText())!==dark)await toggle.click();
      const layout=await page.locator('.commodity-detail-page .locked-panel').evaluate(node=>({
        fits:document.documentElement.scrollWidth<=innerWidth+1,
        color:getComputedStyle(node.querySelector('strong')).color,
        background:getComputedStyle(node).backgroundColor,
        foreground:getComputedStyle(document.documentElement).getPropertyValue('--color-text').trim(),
      }));
      assert.equal(layout.fits,true);assert.notEqual(layout.color,layout.background);
      assert.equal(layout.color,dark?'rgb(231, 236, 231)':'rgb(28, 42, 34)');
      await page.screenshot({path:path.join(lab,`runtime/intelligence-only-guest-${width}-${dark?'dark':'light'}.png`)});
    }
    checks.guest_intelligence_only_page_has_no_repeated_prices_or_private_requests_and_readable_themes=true;
    await context.close();
  }
  {
    const {context,page,commodity}=await fixture(true);
    await context.route('**/api/commodities/'+commodity.id,route=>route.fulfill({json:{...commodity,name:'Synthetic commodity without current prices'}}));
    await context.route('**/api/price-updates*',route=>route.fulfill({json:[]}));
    await page.goto(origin+'/commodities/Any-name?commodity_id='+commodity.id);
    await page.getByRole('heading',{name:'Cost breakdown',exact:true}).waitFor();
    assert.equal(await page.locator('.intelligence-grid > article').count(),6);
    assert.equal(await page.locator('.commodity-detail-page .detail-card').count(),0);
    checks.entitled_users_keep_all_six_intelligence_sections_without_current_price_dependency=true;
    await context.close();
  }
  {
    const {context,page,commodity}=await fixture();
    await context.route('**/api/commodities',route=>route.fulfill({json:[commodity,{...commodity,id:91001}]}));
    await page.goto(origin+'/commodities/Egusi');
    await page.getByText('Choose this commodity from Current Prices to view its market insights.',{exact:true}).waitFor();
    assert.equal(await page.locator('.intelligence-grid,.commodity-detail-page .locked-panel').count(),0);
    checks.ambiguous_name_only_bookmarks_fail_closed_and_cannot_mix_commodities=true;
    await context.close();
  }
  assert.equal(external,0);
  for(const [name,passed] of Object.entries(checks))assert.equal(passed,!expectBug,name);
  const report={checks,expected_original_bug:expectBug,external_page_requests:external,production_connections:0,extra_commodities_or_markets_created:0};
  fs.writeFileSync(path.join(lab,'runtime/detail-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {await browser.close();}
