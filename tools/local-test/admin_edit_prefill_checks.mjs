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
const page=await context.newPage();page.setDefaultTimeout(10000);
async function api(endpoint,method='GET',body){return page.evaluate(async({endpoint,method,body})=>{const response=await fetch('/api'+endpoint,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});return {status:response.status,body:response.status===204?null:await response.json()};},{endpoint,method,body});}
const cases=[
  {endpoint:'market-signals',route:'market-signals',heading:'Market signals',button:'Save market signal',values:{signal_type:'Synthetic saved type',signal_description:'Synthetic saved description',possible_meaning:'Synthetic saved optional note',suggested_action:'Investigate'},edit:'signal_description',clear:'possible_meaning'},
  {endpoint:'quality-signals',route:'quality-signals',heading:'Quality signals',button:'Save quality signal',values:{quality_status:'Synthetic saved status',moisture_status:'Synthetic saved moisture',storage_readiness:'Synthetic saved readiness',risk_note:'Synthetic saved risk'},edit:'quality_status',clear:'risk_note'},
];
try {
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const prices=(await api('/price-updates/admin/history')).body,price=prices[0];
  for(const test of cases){
    const base={commodity_id:price.commodity_id,market_id:price.market_id,price_update_id:price.id,...test.values};
    const rows=[];for(const suffix of ['one','two']){const result=await api('/'+test.endpoint,'POST',{...base,[test.edit]:test.values[test.edit]+' '+suffix});assert.equal(result.status,201);rows.push(result.body);created.push([test.endpoint,result.body.id]);}
    const known=(await api('/'+test.endpoint)).body;
    let release;const held=new Promise(resolve=>{release=resolve;});
    await context.route('**/api/'+test.endpoint,async route=>{await held;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(known)});},{times:1});
    await page.goto(origin+'/admin/'+test.route);await page.getByRole('heading',{name:test.heading,exact:true}).waitFor();
    const form=page.locator('form.admin-form'),id=form.locator('[name=id]');
    await id.fill(String(rows[0].id));
    checks[test.endpoint+'_blocks_until_list_loaded']=await id.evaluate(input=>!input.checkValidity());
    release();await page.getByText('Loading '+test.heading.toLowerCase()+'…',{exact:true}).waitFor({state:'hidden'});
    const field=form.locator('[name='+test.edit+']');
    await page.waitForFunction(()=>document.querySelector('form.admin-form [name=id]').validationMessage!=='Wait for the selected record to load.');
    checks[test.endpoint+'_loads_saved_values']=await field.inputValue()===rows[0][test.edit]&&await form.locator('[name='+test.clear+']').inputValue()===rows[0][test.clear];
    if(!checks[test.endpoint+'_loads_saved_values'])continue;
    const changed='Synthetic changed only one field';await field.fill(changed);
    let response=page.waitForResponse(response=>response.request().method()==='PATCH'&&new URL(response.url()).pathname==='/api/'+test.endpoint+'/'+rows[0].id);
    await form.getByRole('button',{name:test.button,exact:true}).click();assert.equal((await response).status(),200);
    const saved=(await api('/'+test.endpoint+'/'+rows[0].id)).body;
    checks[test.endpoint+'_single_field_edit_preserves_other_values']=Object.keys(base).every(key=>String(saved[key])===String(key===test.edit?changed:base[key]));
    await page.reload();await id.fill(String(rows[0].id));await page.waitForFunction(({name,value})=>document.querySelector('form.admin-form [name='+name+']').value===value,{name:test.edit,value:changed});
    checks[test.endpoint+'_reload_preserves_saved_edit']=await form.locator('[name='+test.clear+']').inputValue()===base[test.clear];
    await form.locator('[name='+test.clear+']').fill('');response=page.waitForResponse(response=>response.request().method()==='PATCH'&&new URL(response.url()).pathname==='/api/'+test.endpoint+'/'+rows[0].id);await form.getByRole('button',{name:test.button,exact:true}).click();assert.equal((await response).status(),200);
    checks[test.endpoint+'_explicit_clearing_remains_possible']=(await api('/'+test.endpoint+'/'+rows[0].id)).body[test.clear]===null;
    await id.fill(String(rows[1].id));await page.waitForFunction(({name,value})=>document.querySelector('form.admin-form [name='+name+']').value===value,{name:test.edit,value:rows[1][test.edit]});
    checks[test.endpoint+'_switching_id_loads_other_record']=await form.locator('[name='+test.clear+']').inputValue()===base[test.clear];
    await id.fill('999999');await page.locator('main .status-box.error').filter({hasText:'Record not found. Enter an existing ID or leave it blank to create.'}).waitFor();
    checks[test.endpoint+'_unknown_id_blocks_wrong_record_submit']=await id.evaluate(input=>!input.checkValidity())&&await field.inputValue()==='';
    await id.fill('');checks[test.endpoint+'_blank_id_restores_creation_defaults']=await field.inputValue()===''&&await id.evaluate(input=>input.checkValidity());
    for(const [key,value] of Object.entries(base)){
      const control=form.locator('[name='+key+']');
      if(await control.evaluate(element=>element.tagName==='SELECT'))await control.selectOption(String(value));else await control.fill(String(value));
    }
    response=page.waitForResponse(response=>response.request().method()==='POST'&&new URL(response.url()).pathname==='/api/'+test.endpoint);await form.getByRole('button',{name:test.button,exact:true}).click();const added=await response;assert.equal(added.status(),201);created.push([test.endpoint,(await added.json()).id]);checks[test.endpoint+'_original_creation_still_works']=true;
  }
  assert.deepEqual((await api('/price-updates/admin/history')).body,prices);assert.equal(outside,0);
  const failures=Object.entries(checks).filter(([,value])=>!value).map(([name])=>name);
  const report={checks,failures,expected_original_bug:expectBug,original_price_history_unchanged:true,external_page_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/admin-edit-prefill-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(expectBug)assert.ok(failures.length>0);else assert.deepEqual(failures,[]);
} finally {for(const [endpoint,id] of created.reverse())await api('/'+endpoint+'/'+id,'DELETE').catch(()=>{});await browser.close();}
