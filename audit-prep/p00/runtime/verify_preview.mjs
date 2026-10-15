import assert from 'node:assert/strict';
import { pathToFileURL } from 'node:url';
import path from 'node:path';
import fs from 'node:fs/promises';
const lab=path.resolve(process.argv[2]);
const {path:snapshot}=JSON.parse(await fs.readFile(path.join(lab,'runtime/frontend-snapshot.json'),'utf8'));
const {chromium}=await import(pathToFileURL(path.join(snapshot,'node_modules/playwright/index.mjs')));
const origin='http://127.0.0.1:55442';
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const external=[];
async function pageFor(){
 const context=await browser.newContext({serviceWorkers:'block'});
 await context.routeWebSocket('**/*',ws=>ws.close());
 await context.route('**/*',async route=>{const url=new URL(route.request().url());if(url.origin!==origin){external.push(url.origin);return route.abort('blockedbyclient');}return route.continue();});
 await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
 const page=await context.newPage();page.setDefaultTimeout(10000);
 return {context,page};
}
try{
 const guest=await pageFor();
 await guest.page.goto(origin+'/prices');
 await guest.page.getByRole('heading',{name:'Egusi',exact:true}).first().waitFor();
 assert.match(await guest.page.locator('body').innerText(),/SYNTHETIC DATA ONLY/);
 const publicProof=await guest.page.evaluate(async()=>{
  const current=await(await fetch('/api/price-updates')).json();
  const history=await fetch('/api/price-updates/history');
  return {current_rows:current.length,history_status:history.status,sources_hidden:current.every(x=>!('source_1' in x)&&!('source_2' in x))};
 });
 assert.equal(publicProof.current_rows,6);assert.ok([401,403].includes(publicProof.history_status));assert.equal(publicProof.sources_hidden,true);
 await guest.context.close();
 for(const role of ['trial','admin']){
  const item=await pageFor();
  await item.page.goto(origin+'/login');
  await item.page.getByLabel('Email',{exact:true}).fill(role+'@example.com');
  await item.page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await item.page.getByRole('button',{name:'Log in',exact:true}).click();
  await item.page.waitForURL('**/dashboard');
  if(role==='trial'){
    await item.page.getByRole('button',{name:'\u20a62,500 / 30 days',exact:true}).waitFor();
    await item.page.goto(origin+'/history');
    await item.page.getByRole('heading',{name:/history/i}).first().waitFor();
  } else {
    await item.page.goto(origin+'/admin/users');
    await item.page.getByText('Demo Reporter',{exact:true}).filter({visible:true}).waitFor();
  }
  await item.page.screenshot({path:path.join(lab,'artifacts/preview-'+role+'.png'),fullPage:true});
  await item.context.close();
 }
 assert.deepEqual(external,[]);
 const result={real_api_preview:true,guest:publicProof,trial_login:true,admin_login_and_user_list:true,production_connections:0};
 await fs.writeFile(path.join(lab,'artifacts/local-preview-proof.json'),JSON.stringify(result,null,2));
 console.log(JSON.stringify(result));
}finally{await browser.close();}
