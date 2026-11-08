import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const before=process.argv.includes('--expect-bug');
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const results=[];
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
try {
  await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
  const original=await page.evaluate(()=>fetch('/api/price-updates').then(response=>response.json()));
  const normalGeometry=[];
  for(const width of [375,1366]) {
    await page.setViewportSize({width,height:900});
    await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
    normalGeometry.push({width,card:await page.locator('.price-card').first().boundingBox(),badge:await page.locator('.price-card .movement').first().boundingBox()});
  }
  // Browser-only HTTP stubs use existing text fields at their existing limits.
  // No records, names, measurements, prices or demo fixtures are saved/changed.
  const long=original.map(item=>({...item,commodity:{...item.commodity,name:'Synthetic'+ 'x'.repeat(91)},market:{...item.market,name:'Synthetic'+ 'x'.repeat(141)}}));
  await page.route(origin+'/api/price-updates',route=>route.fulfill({json:long}));
  for(const width of [320,375,640,768,900,1366])for(const easy of [false,true]) {
    await page.setViewportSize({width,height:900});
    await page.evaluate(easy=>localStorage.setItem('priceyard_easy_reading',easy?'1':'0'),easy);
    await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
    const state=await page.evaluate(()=>{
      const outliers=[];
      for(const node of document.querySelectorAll('.page input,.page select,.page button,.price-card h3,.price-card .card-row,.price-card .price-range')) {
        const box=node.getBoundingClientRect();if(!box.width||!box.height)continue;
        if(box.left < -1||box.right > innerWidth+1||node.scrollWidth>node.clientWidth+1)outliers.push({tag:node.tagName,field:node.getAttribute('name')||node.className,left:Math.round(box.left),right:Math.round(box.right),content:node.scrollWidth,box:node.clientWidth});
      }
      return {document_overflow:document.documentElement.scrollWidth>innerWidth+1,outliers};
    });
    results.push({width,easy,...state});
  }
  await page.unroute(origin+'/api/price-updates');
  assert.deepEqual(await page.evaluate(()=>fetch('/api/price-updates').then(response=>response.json())),original);
  assert.equal(outside,0);
  if(!before)assert.deepEqual(normalGeometry,JSON.parse(fs.readFileSync(path.join(lab,'runtime/mobile-content-checks-before.json'),'utf8')).normal_geometry);
  const report={before,cases:results.length,failures:results.filter(row=>row.document_overflow||row.outliers.length),normal_geometry:normalGeometry,normal_card_geometry_preserved:!before,server_records_unchanged:true,measurements_unchanged:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/mobile-content-checks'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(!before)assert.equal(report.failures.length,0);
} finally {await browser.close();}
