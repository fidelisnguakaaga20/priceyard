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
  for(const name of ['trial','paid','manual-paid']) {
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
    await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
    const page=await context.newPage();
    page.setDefaultTimeout(12000);
    await page.clock.install({time:new Date()});
    await page.goto(origin+'/login');
    await page.getByLabel('Email',{exact:true}).fill(name+'@example.com');
    await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();
    await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
    const subscription=await page.evaluate(async()=>{
      const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
      const headers={Authorization:'Bearer '+token};
      const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
      return fetch('/api/subscriptions/'+user.id,{headers}).then(r=>r.json());
    });
    await page.goto(origin+'/history');
    await page.locator('.history-table-view tbody tr').first().waitFor();
    // Legacy API datetimes without offsets are UTC in the backend, while the
    // Windows checker defaults to Lagos local time. Use an explicit UTC oracle.
    const trialEnd=subscription.trial_ends_at;
    const expiry=name==='trial'?Date.parse(/(?:Z|[+-]\d{2}:\d{2})$/i.test(trialEnd)?trialEnd:trialEnd+'Z'):name==='paid'?Date.parse(subscription.end_date+'T00:00:00Z')+86400000:Date.now()+365*86400000;
    if(name==='manual-paid')await page.clock.setSystemTime(new Date(expiry));
    else await page.clock.setSystemTime(new Date(expiry-3000));
    // Simulate returning to the tab near its deadline. Run the short remaining
    // timer normally so React effects settle; avoid skipping a month of timers.
    await page.evaluate(()=>window.dispatchEvent(new Event('focus')));
    await page.clock.runFor(4000);
    if(name==='manual-paid') {
      assert.equal(subscription.end_date,null);
      await page.locator('.history-table-view tbody tr').first().waitFor();
      assert.equal(await page.locator('.locked-panel').count(),0);
      result[name]={indefinite_original_grant_preserved:true};
    } else {
      await page.locator('.locked-panel').waitFor();
      assert.equal(await page.locator('.history-table-view tbody tr').count(),0);
      assert.ok((await page.locator('body').innerText()).includes('Access: Free'));
      result[name]={client_deadline_timer_hides_history_without_reload:true};
    }
    await context.close();
  }
  const report={result,scope:'Browser clock only; backend clock unchanged. Backend expiry separately tested.',production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/expiry-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{await browser.close();}
