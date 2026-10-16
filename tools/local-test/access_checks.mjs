import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const result={};
try {
  for (const name of ['guest','free','trial','paid','reporter','admin','expired-reporter','expired-paid-reporter']) {
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
    await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
    const page=await context.newPage();
    page.setDefaultTimeout(12000);
    if (name!=='guest') {
      await page.goto(origin+'/login');
      await page.getByLabel('Email',{exact:true}).fill(name+'@example.com');
      await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
      await page.getByRole('button',{name:'Log in',exact:true}).click();
      await page.waitForURL('**/dashboard');
      await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
    }
    await page.goto(origin+'/prices');
    await page.locator('.price-card').first().waitFor();
    const access=await page.evaluate(async()=>{
      const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
      const headers=token?{Authorization:'Bearer '+token}:{};
      const current=await fetch('/api/price-updates').then(r=>r.json());
      const date=new Date(new Date(current[0].update_date_time).getTime()-86400000).toISOString().slice(0,10);
      const urls=['/price-updates/history','/price-updates?date='+date,'/price-updates/comparison?commodity=Egusi&date='+date,'/price-updates/1','/quality-signals','/quality-signals/1'];
      const statuses=[];
      for(const url of urls)statuses.push((await fetch('/api'+url,{headers})).status);
      return {statuses,current,detail:(await fetch('/api/price-updates/'+current[0].id)).status};
    });
    const entitled=['trial','paid','admin'].includes(name);
    const denied=name==='guest'?401:403;
    assert.deepEqual(access.statuses,entitled?[200,200,200,200,200,404]:Array(6).fill(denied));
    assert.equal(access.detail,200);
    assert.equal(access.current[0].commodity.name,'Egusi');
    assert.equal(access.current[0].bag_size,null);
    assert.equal(Number(access.current[0].previous_price_low),210000);
    assert.ok(!('source_1' in access.current[0]));
    await page.goto(origin+'/commodities/Egusi');
    await page.getByRole('heading',{name:'Egusi',exact:true}).waitFor();
    await page.locator('.detail-card').first().waitFor();
    assert.equal(await page.getByText(/Grade:/).count(),0);
    if(entitled)await page.getByRole('heading',{name:'Quality readiness',exact:true}).waitFor();
    await page.goto(origin+'/history');
    await page.getByRole('heading',{name:'Price history',exact:true}).waitFor();
    if(entitled)await page.locator('.history-table-view tbody tr').first().waitFor();
    result[name]={historical_status:access.statuses[0],alternate_routes_protected:true,original_current_cards:true,original_detail_page:true};
    await context.close();
  }
  const report={result,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/access-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
} finally {await browser.close();}
