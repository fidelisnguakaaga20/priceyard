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
try{
  for(const name of ['expired-reporter','expired-paid-reporter']){
    const context=await browser.newContext({serviceWorkers:'block'});
    await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
    await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
    const page=await context.newPage();
    page.setDefaultTimeout(10000);
    await page.goto(origin+'/login');
    await page.getByLabel('Email',{exact:true}).fill(name+'@example.com');
    await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
    await page.getByRole('button',{name:'Log in',exact:true}).click();
    await page.waitForURL('**/dashboard');
    await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
    const access=await page.evaluate(async()=>{
      const token=localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token');
      const headers={Authorization:'Bearer '+token};
      const first=await fetch('/api/auth/me',{headers}).then(r=>r.json());
      const subscription=await fetch('/api/subscriptions/'+first.id,{headers}).then(r=>r.json());
      const user=await fetch('/api/auth/me',{headers}).then(r=>r.json());
      const history=await fetch('/api/price-updates/history',{headers});
      return {status:subscription.status,role:user.role,history_status:history.status};
    });
    assert.deepEqual(access,{status:'expired',role:'reporter',history_status:403});
    await page.goto(origin+'/report-price');
    await page.getByRole('heading',{name:/report.*price/i}).first().waitFor();
    await page.locator('form').first().waitFor();
    assert.equal(await page.getByLabel(/grade/i).count(),0);
    await page.screenshot({path:path.join(lab,'runtime/'+name+'.png'),fullPage:true});
    result[name]={...access,existing_report_form_visible:true};
    await context.close();
  }
  const report={result,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/staff-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{await browser.close()}
