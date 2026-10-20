// Browser transport check only. Every page request is fulfilled locally or
// aborted; never contact Render, a database or any external provider.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(lab,'../..');
const {chromium}=await import(pathToFileURL(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const front='https://priceyard.onrender.com',back='https://priceyard-api.onrender.com';
let browser;
const report={scope:'virtual browser cookie routing only',real_network_requests_allowed:0,production_access:false,application_changed:false,cases:[]};
try{
  browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
  for(const sameOrigin of [false,true]){
    const context=await browser.newContext({serviceWorkers:'block'});
    const base=sameOrigin?front+'/api':back;
    await context.route('**/*',async route=>{
      const request=route.request(),url=new URL(request.url());
      if(![front,back].includes(url.origin))return route.abort();
      const headers={'Access-Control-Allow-Origin':front,'Access-Control-Allow-Credentials':'true','Access-Control-Allow-Methods':'GET, POST','Access-Control-Allow-Headers':'content-type','Content-Type':'application/json'};
      if(request.method()==='OPTIONS')return route.fulfill({status:204,headers});
      if(request.url()===front+'/')return route.fulfill({status:200,contentType:'text/html',body:'<!doctype html><title>Synthetic routing fixture</title>'});
      if(request.url()===base+'/auth/browser/login')return route.fulfill({status:200,headers:{...headers,'Set-Cookie':'__Host-priceyard_session=synthetic-release-fixture; Path=/; Secure; HttpOnly; SameSite=Lax'},body:'{}'});
      if(request.url()===base+'/auth/browser/session'){
        const cookie=(await request.allHeaders()).cookie||'';
        const present=cookie.includes('__Host-priceyard_session=synthetic-release-fixture');
        return route.fulfill({status:present?200:401,headers,body:JSON.stringify({cookie_present:present})});
      }
      return route.abort();
    });
    const page=await context.newPage();page.setDefaultTimeout(8000);
    await page.goto(front+'/');
    const result=await page.evaluate(async base=>{
      const login=await fetch(base+'/auth/browser/login',{method:'POST',credentials:'include',headers:{'Content-Type':'application/json'},body:'{}'});
      const session=await fetch(base+'/auth/browser/session',{credentials:'include'});
      return {login_response:login.status,session_response:session.status,cookie_present:(await session.json()).cookie_present};
    },base);
    if(result.login_response!==200||result.cookie_present!==sameOrigin||result.session_response!==(sameOrigin?200:401))throw Error('Unexpected cookie routing result');
    report.cases.push({topology:sameOrigin?'same_origin_API_path':'direct_separate_Render_sites',...result});
    await context.close();
  }
  report.status='passed_expected_browser_transport_contract';
}catch(error){report.status='not_verified';report.error_type=error.name;}
finally{if(browser)await browser.close();}
fs.writeFileSync(path.join(lab,'runtime/provider-tunnel-20261020/release-cookie-routing.json'),JSON.stringify(report,null,2));
process.stdout.write(JSON.stringify(report));
