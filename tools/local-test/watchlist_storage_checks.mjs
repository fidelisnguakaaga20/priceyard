import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug');
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;const created=[],checks={};
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(10000);const pageErrors=[];page.on('pageerror',error=>pageErrors.push(error.message));
async function api(endpoint,method='GET',body){return page.evaluate(async({endpoint,method,body})=>{
  const response=await fetch('/api'+endpoint,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
  return {status:response.status,body:response.status===204?null:await response.json()};
},{endpoint,method,body});}
try{
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('free@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const before=(await api('/price-updates')).body,commodity=(await api('/commodities')).body.find(row=>row.name==='Egusi');
  const original=(await api('/watchlist')).body;
  await page.goto(origin+'/watchlist');const form=page.locator('form.filter-bar');
  await form.getByRole('combobox',{name:/^Commodity/}).selectOption(String(commodity.id));
  const target=form.getByLabel('Only alert me at a price (optional)',{exact:true});
  await target.fill('1000000000000');let response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/watchlist');
  await form.getByRole('button',{name:'Save item',exact:true}).click();const oversized=await response;
  if(oversized.status()===201){const row=await oversized.json();created.push(row.id);await api('/watchlist/'+row.id,'DELETE');}
  checks.out_of_range_uses_existing_form_error=oversized.status()===422;
  if(!expectBug)await page.locator('.status-box.error').filter({hasText:'Decimal input'}).waitFor();
  const precise=await api('/watchlist','POST',{commodity_id:commodity.id,target_price:'210000.001',target_direction:'at_or_below'});
  if(precise.status===201){created.push(precise.body.id);await api('/watchlist/'+precise.body.id,'DELETE');}
  checks.target_is_not_silently_rounded=precise.status===422;
  checks.invalid_targets_leave_existing_watchlist_unchanged=JSON.stringify((await api('/watchlist')).body)===JSON.stringify(original);
  await page.reload();await form.getByRole('combobox',{name:/^Commodity/}).selectOption(String(commodity.id));await target.fill('210000');
  response=page.waitForResponse(r=>r.request().method()==='POST'&&new URL(r.url()).pathname==='/api/watchlist');await form.getByRole('button',{name:'Save item',exact:true}).click();const added=await response;assert.equal(added.status(),201);const row=await added.json();created.push(row.id);
  checks.original_whole_naira_target_still_saves=Number(row.target_price)===210000&&row.target_direction==='at_or_below';
  await page.reload();await page.getByText('Alert when',{exact:false}).waitFor();checks.target_survives_page_reload=(await api('/watchlist')).body.some(item=>item.id===row.id&&Number(item.target_price)===210000);
  assert.equal((await api('/watchlist/'+row.id,'DELETE')).status,204);
  checks.original_watchlist_and_prices_preserved=JSON.stringify((await api('/watchlist')).body)===JSON.stringify(original)&&JSON.stringify((await api('/price-updates')).body)===JSON.stringify(before);
  assert.equal(outside,0);const failures=Object.entries(checks).filter(([,ok])=>!ok).map(([key])=>key);
  const report={checks,failures,expected_original_bug:expectBug,external_page_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/watchlist-storage-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(expectBug)assert.ok(failures.length>0);else assert.deepEqual(failures,[]);
}catch(error){console.log(JSON.stringify({url:page.url(),pageErrors,forms:await page.locator('form').evaluateAll(forms=>forms.map(form=>({className:form.className,labels:Array.from(form.querySelectorAll('label')).map(label=>label.textContent)})))}));throw error;
}finally{for(const id of created)await api('/watchlist/'+id,'DELETE').catch(()=>{});await browser.close();}
