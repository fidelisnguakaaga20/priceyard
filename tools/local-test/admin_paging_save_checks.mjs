import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446',before=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
function deferred(){let resolve;const promise=new Promise(r=>resolve=r);return {promise,resolve};}
try{
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
 await page.goto(origin+'/__test__/admin-paging');await page.getByRole('button',{name:'Load synthetic sample',exact:true}).click();await page.getByRole('status').getByText('205 synthetic users and205 synthetic payments ready.',{exact:true}).waitFor();
 await page.goto(origin+'/admin/users?offset=100');await page.waitForFunction(()=>document.querySelectorAll('.admin-table-view tbody tr').length===100);
 const target=await page.evaluate(async()=>{const r=await fetch('/api/users/page?offset=100',{headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token')}});return(await r.json()).items[0];});
 const ready=deferred(),release=deferred();
 await context.route(origin+'/api/users/'+target.id,async route=>{assert.equal(route.request().method(),'PATCH');ready.resolve();await release.promise;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify({...target,is_active:false})});});
 await page.locator('.admin-table-view tbody tr').filter({hasText:target.email}).getByRole('button',{name:'Deactivate',exact:true}).click();await ready.promise;
 await page.getByRole('button',{name:'Next',exact:true}).click();await page.waitForFunction(()=>document.querySelectorAll('.admin-table-view tbody tr').length===5);
 const refreshed=page.waitForRequest(request=>new URL(request.url()).pathname==='/api/users/page'&&request.method()==='GET');
 release.resolve();const request=await refreshed,offset=new URL(request.url()).searchParams.get('offset');
 assert.equal(offset,before?'100':'200');
 if(!before){await page.waitForFunction(()=>document.querySelectorAll('.admin-table-view tbody tr').length===5);await page.getByRole('button',{name:'Previous',exact:true}).waitFor({state:'visible'});assert.equal(new URL(page.url()).searchParams.get('offset'),'200');assert.equal(await page.getByRole('button',{name:'Previous',exact:true}).isEnabled(),true);}
 assert.equal(outside,0);
 const report={before,pending_save_then_navigation_reproduced:true,completion_reloads_current_page:offset==='200',actual_reload_offset:Number(offset),synthetic_patch_response_only:true,underlying_user_not_modified:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/admin-paging-save'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
