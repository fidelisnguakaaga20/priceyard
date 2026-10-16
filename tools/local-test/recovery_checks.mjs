// Fault only the initial browser price response; recovery uses the real local API.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const expectBug=process.argv.includes('--expect-bug');
const result={};
try {
  for(const routePath of ['/','/prices']){
    const context=await browser.newContext({serviceWorkers:'block'});
    await context.addInitScript(()=>{
      localStorage.setItem('priceyard_onboarding_seen','1');
      const original=window.setInterval.bind(window);
      const clear=window.clearInterval.bind(window);
      window.__priceyardRefreshCallbacks=new Map();
      window.setInterval=(callback,delay,...args)=>{
        const id=original(callback,delay,...args);
        if(delay===60000&&typeof callback==='function')window.__priceyardRefreshCallbacks.set(id,()=>callback(...args));
        return id;
      };
      window.clearInterval=id=>{window.__priceyardRefreshCallbacks.delete(id);return clear(id)};
    });
    let failing=true;
    let recovered=0;
    await context.route('**/*',async route=>{
      const url=new URL(route.request().url());
      if(url.origin!==origin)return route.abort();
      if(url.pathname==='/api/price-updates'){
        if(failing)return route.fulfill({status:503,contentType:'application/json',body:JSON.stringify({detail:'Synthetic temporary outage'})});
        recovered++;
      }
      return route.continue();
    });
    const page=await context.newPage();
    page.setDefaultTimeout(10000);
    await page.goto(origin+routePath);
    await page.locator('.status-box.error').filter({hasText:'Synthetic temporary outage'}).waitFor();
    failing=false;
    const recoveredResponse=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/price-updates'&&response.status()===200);
    await page.evaluate(()=>{if(!window.__priceyardRefreshCallbacks.size)throw Error('No real refresh interval registered');for(const callback of window.__priceyardRefreshCallbacks.values())callback()});
    assert.equal((await (await recoveredResponse).json()).length,1);
    if(expectBug)await page.locator('.status-box.error').waitFor();
    else{
      await page.locator('.status-box.error').waitFor({state:'hidden'});
      await page.locator('.price-card').first().waitFor();
    }
    const lingering=await page.locator('.status-box.error').count();
    assert.ok(recovered>0,'Recovery must make a real request to the local API');
    assert.equal(lingering,expectBug?1:0,routePath+' recovery error state');
    result[routePath]={initial_failure_visible:true,real_api_recovered:true,error_cleared:lingering===0};
    await page.screenshot({path:path.join(lab,'runtime/recovery-'+(routePath==='/'?'home':'prices')+(expectBug?'-before':'-after')+'.png')});
    await context.close();
  }
  const report={expected_original_defect:expectBug,result,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/recovery-'+(expectBug?'before':'after')+'.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{await browser.close()}
