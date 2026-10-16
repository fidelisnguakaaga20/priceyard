import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
const page=await context.newPage();page.setDefaultTimeout(12000);
try {
  await page.goto(origin+'/__test__/push');
  await page.getByRole('button',{name:'Check device ownership protection',exact:true}).click();
  await page.waitForFunction(()=>window.__pushOwnershipResult?.complete);
  const checks=await page.evaluate(()=>window.__pushOwnershipResult);
  assert.equal(checks.passed,true);assert.equal(checks.rejected,409);assert.equal(outside,0);
  const status=await page.evaluate(()=>fetch('/__test__/status').then(r=>r.json()));assert.equal(status.providers,'disabled');
  const report={checks,external_page_requests:outside,real_notification_deliveries:0,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/push-ownership-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
