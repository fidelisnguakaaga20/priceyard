import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)), origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const before=process.argv.includes('--expect-bug');
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
let outside=0;const results=[];
try {
  for (const easy of [false,true]) {
    const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
    await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
    await context.addInitScript(easy=>{
      localStorage.setItem('priceyard_onboarding_seen','1');
      localStorage.setItem('priceyard_easy_reading',easy?'1':'0');
    },easy);
    const page=await context.newPage();page.setDefaultTimeout(15000);
    async function measure(screen,width) {
      await page.setViewportSize({width,height:900});await page.goto(origin+screen);
      await page.locator('main h1').first().waitFor();
      await page.locator('main .loading-indicator').waitFor({state:'hidden'});
      await page.waitForFunction(()=>!document.querySelector('main [aria-busy="true"]'));
      const state=await page.evaluate(()=>{
        const outliers=[];
        for(const node of document.querySelectorAll('main input,main select,main textarea,main button,main .admin-metric,.menu-button,.display-toggles button')) {
          const box=node.getBoundingClientRect();
          if(!box.width||!box.height||getComputedStyle(node).visibility==='hidden'||node.closest('.table-wrap'))continue;
          if(box.left < -1||box.right > innerWidth+1)outliers.push({tag:node.tagName,name:node.getAttribute('name')||node.textContent?.trim().slice(0,80),left:Math.round(box.left),right:Math.round(box.right)});
        }
        return {document_overflow:document.documentElement.scrollWidth>innerWidth+1,outliers,admin_cards:document.querySelectorAll('.admin-metric').length};
      });
      results.push({screen,width,easy,...state});
    }
    for(const width of [320,375,768])for(const screen of ['/prices','/login','/register','/forgot-password'])await measure(screen,width);
    await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
    for(const width of [320,375,768])for(const screen of ['/dashboard','/history','/commodities/Egusi','/admin','/admin/prices','/admin/users','/admin/subscriptions','/admin/audit','/admin/costs'])await measure(screen,width);
    await context.close();
  }
  const failures=results.filter(row=>row.document_overflow||row.outliers.length);
  const report={before,cases:results.length,failures,all_fourteen_cards_retained:results.filter(row=>row.screen==='/admin').every(row=>row.admin_cards===14),external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/mobile-checks'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(!before){assert.equal(failures.length,0);assert.equal(report.all_fourteen_cards_retained,true);}
  assert.equal(outside,0);
} finally {await browser.close();}
