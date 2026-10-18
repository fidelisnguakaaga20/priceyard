import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';let outside=0;const cases=[];
try {
 for(const timezoneId of ['Africa/Lagos','UTC']){
  const context=await browser.newContext({timezoneId,serviceWorkers:'block',extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()}});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
  await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  const page=await context.newPage();page.setDefaultTimeout(15000);
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const saved=await page.evaluate(async()=>{
   const headers={Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')};
   return {current:await fetch('/api/price-updates').then(r=>r.json()),history:await fetch('/api/price-updates/history',{headers}).then(r=>r.json())};
  });
  // PostgreSQL returns aware TIMESTAMPTZ; SQLite preview intentionally does not.
  // Mock only response timestamps to exercise native-shaped instants in the UI.
  let timestamp='2000-12-31T23:30:00Z';
  await context.route(origin+'/api/price-updates**',route=>{
   const url=new URL(route.request().url());
   if(!['/api/price-updates','/api/price-updates/history'].includes(url.pathname))return route.continue();
   const rows=(url.pathname.endsWith('/history')?saved.history:saved.current).map(row=>({...row,update_date_time:timestamp}));
   return route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(rows)});
  });
  for(const pathname of ['/prices','/history']){
   await page.goto(origin+pathname);
   await page.getByText(/1 Jan 2001.*12:30.*am WAT/).first().waitFor();
   assert.ok(!(await page.locator('main').innerText()).includes('31 Dec 2000'));
   await page.setViewportSize({width:375,height:812});
   await page.getByText(/1 Jan 2001.*12:30.*am WAT/).filter({visible:true}).first().waitFor();
   assert.ok(await page.evaluate(()=>document.documentElement.scrollWidth<=window.innerWidth+1));
   await page.setViewportSize({width:1280,height:900});
  }
  timestamp='2000-12-31T23:30:00';
  await page.goto(origin+'/prices');await page.getByText(timestamp,{exact:true}).first().waitFor();
  assert.ok(!(await page.locator('main').innerText()).includes('12:30 am WAT'));
  const unchanged=await page.evaluate(()=>fetch('/api/price-updates/admin/history',{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}}).then(r=>r.json()));
  // Verify timestamps specifically using unmocked Admin history; the display mock
  // never writes an epoch, quantity or source into the database.
  for(const row of saved.history)assert.equal(unchanged.find(item=>item.id===row.id).update_date_time,row.update_date_time);
  cases.push({timezone:timezoneId,wat_midnight_display:true,mobile_history_and_cards:true,ambiguous_legacy_value_not_guessed:true,stored_timestamps_unchanged:true});
  await context.close();
 }
 assert.equal(outside,0);
 const report={cases,external_requests:outside,production_connections:0,aware_timestamps_response_mock_only:true};
 fs.writeFileSync(path.join(lab,'runtime/price-display-time-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
