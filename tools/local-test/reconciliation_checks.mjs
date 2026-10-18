import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
async function trigger(mode){return page.evaluate(async mode=>{const response=await fetch('/__test__/reconciliation',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({mode})});if(!response.ok)throw Error('Synthetic recovery failed');return response.json();},mode);}
try{
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('verify@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const preview=await trigger('preview');assert.equal(preview.provider_calls,0);assert.equal(preview.payment_status,'pending');assert.equal(preview.subscription_status,'free');
  const wrong=await trigger('wrong_amount');assert.equal(wrong.report.outcomes[0].outcome,'error');assert.equal(wrong.payment_status,'pending');assert.equal(wrong.subscription_status,'free');
  await page.reload();await page.getByRole('heading',{name:'Welcome, Test Verify',exact:true}).waitFor();
  assert.ok(!(await page.locator('body').innerText()).includes('Active Paid'));
  const recovered=await trigger('valid');assert.equal(recovered.report.outcomes[0].outcome,'confirmed');assert.equal(recovered.subscription_status,'active');
  await page.reload();await page.getByRole('heading',{name:'Welcome, Test Verify',exact:true}).waitFor();assert.ok((await page.locator('body').innerText()).includes('Active Paid'));
  const historyStatus=await page.evaluate(async()=>{const response=await fetch('/api/price-updates/history');return response.status;});assert.equal(historyStatus,200);
  const repeated=await trigger('valid');assert.equal(repeated.provider_calls,0);assert.equal(repeated.end_date,recovered.end_date);assert.equal(outside,0);
  const report={dry_run_never_verifies_or_activates:true,mismatched_evidence_stays_pending:true,missed_webhook_recovers_without_callback:true,original_dashboard_and_history_access_reflect_recovery:true,repeated_job_does_not_recredit:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/reconciliation-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
