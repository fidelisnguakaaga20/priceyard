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
function sameValue(actual,expected){return typeof expected==='number'?actual!==null&&actual!==''&&Number(actual)===expected:actual===expected;}
async function waitForField(name,value,numeric){
  await page.waitForFunction(({name,value,numeric})=>{
    const actual=document.querySelector('form.admin-form [name='+name+']').value;
    return numeric?actual!==''&&Number(actual)===Number(value):actual===String(value);
  },{name,value,numeric:!!numeric});
}
const cases=[
  {endpoint:'market-signals',route:'market-signals',heading:'Market signals',button:'Save market signal',values:{signal_type:'Synthetic saved type',signal_description:'Synthetic saved description',possible_meaning:'Synthetic saved optional note',suggested_action:'Investigate'},edit:'signal_description',clear:'possible_meaning',requiredFields:['commodity_id','market_id','signal_type','signal_description']},
  {endpoint:'quality-signals',route:'quality-signals',heading:'Quality signals',button:'Save quality signal',values:{quality_status:'Synthetic saved status',moisture_status:'Synthetic saved moisture',storage_readiness:'Synthetic saved readiness',risk_note:'Synthetic saved risk'},edit:'quality_status',clear:'risk_note',requiredFields:['commodity_id','market_id']},
  {endpoint:'buying-zones',route:'buying-zones',heading:'Buying zones',button:'Save buying zone',values:{price_low:100,price_high:200,reason:'Synthetic saved reason',valid_from:'2026-10-01',valid_to:'2026-10-31',confidence:'Synthetic confidence'},edit:'reason',clear:'valid_to',linkedPrice:false,canDelete:false,requiredFields:['commodity_id','market_id','price_low','price_high','reason','confidence']},
  {endpoint:'sell-watch-windows',route:'sell-watch',heading:'Sell-watch windows',button:'Save sell-watch window',values:{start_period:'Synthetic start',end_period:'Synthetic saved end',observation:'Synthetic saved observation',confidence:'Synthetic confidence'},edit:'observation',clear:'end_period',linkedPrice:false,canDelete:false,requiredFields:['commodity_id','market_id','start_period','observation','confidence']},
  {endpoint:'storage-suitability',route:'storage',heading:'Storage suitability',button:'Save storage suitability',values:{suitability_status:'watch',import_risk:'Synthetic import note',oversupply_risk:'Synthetic supply note',spoilage_risk:'Synthetic spoilage note',buyer_availability:'Synthetic buyer note',quality_storage_notes:'Synthetic saved storage note',summary:'Synthetic saved summary'},edit:'summary',clear:'quality_storage_notes',canDelete:false,requiredFields:['commodity_id','market_id','suitability_status']},
  {endpoint:'cost-breakdowns',route:'costs',heading:'Cost breakdown',button:'Save cost breakdown',values:{transport:120.50,warehouse:80.25,security:0,market_charges:20.75,loading_offloading:30,other_costs:10.10,purchase_price_reference:210000},edit:'transport',clear:'warehouse',linkedPrice:false,numeric:true,requiredFields:['commodity_id','market_id','transport','warehouse','security','market_charges','loading_offloading','other_costs','purchase_price_reference']},
];
try {
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');
  const prices=(await api('/price-updates/admin/history')).body,price=prices[0];
  for(const test of cases){
    const base={commodity_id:price.commodity_id,market_id:price.market_id,...(test.linkedPrice===false?{}:{price_update_id:price.id}),...test.values};
    const rows=[];for(const suffix of ['one','two']){const result=await api('/'+test.endpoint,'POST',{...base,[test.edit]:test.numeric?test.values[test.edit]+(suffix==='one'?1:2):test.values[test.edit]+' '+suffix});assert.equal(result.status,201);rows.push(result.body);created.push([test.endpoint,result.body.id,test.canDelete!==false]);}
    const known=(await api('/'+test.endpoint)).body;
    if(test.requiredFields){
      const audits=(await api('/audit-logs')).body;let rejected=true;
      for(const field of test.requiredFields){const invalid=await api('/'+test.endpoint+'/'+rows[0].id,'PATCH',{[field]:null});rejected=invalid.status===422&&rejected;}
      checks[test.endpoint+'_required_null_values_rejected']=rejected;
      checks[test.endpoint+'_invalid_edits_preserve_records_and_audits']=JSON.stringify((await api('/'+test.endpoint)).body)===JSON.stringify(known)&&JSON.stringify((await api('/audit-logs')).body)===JSON.stringify(audits);
    }
    let release;const held=new Promise(resolve=>{release=resolve;});
    await context.route('**/api/'+test.endpoint,async route=>{await held;await route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(known)});},{times:1});
    await page.goto(origin+'/admin/'+test.route);await page.getByRole('heading',{name:test.heading,exact:true}).waitFor();
    const form=page.locator('form.admin-form'),id=form.locator('[name=id]');
    await id.fill(String(rows[0].id));
    checks[test.endpoint+'_blocks_until_list_loaded']=await id.evaluate(input=>!input.checkValidity());
    release();
    const field=form.locator('[name='+test.edit+']');
    await page.waitForFunction(()=>document.querySelector('form.admin-form [name=id]').validationMessage!=='Wait for the selected record to load.');
    checks[test.endpoint+'_loads_saved_values']=sameValue(await field.inputValue(),test.numeric?Number(rows[0][test.edit]):rows[0][test.edit])&&sameValue(await form.locator('[name='+test.clear+']').inputValue(),test.numeric?Number(rows[0][test.clear]):rows[0][test.clear]);
    if(!checks[test.endpoint+'_loads_saved_values'])continue;
    const changed=test.numeric?321.75:'Synthetic changed only one field';await field.fill(String(changed));
    let response=page.waitForResponse(response=>response.request().method()==='PATCH'&&new URL(response.url()).pathname==='/api/'+test.endpoint+'/'+rows[0].id);
    await form.getByRole('button',{name:test.button,exact:true}).click();assert.equal((await response).status(),200);
    const saved=(await api('/'+test.endpoint+'/'+rows[0].id)).body;
    checks[test.endpoint+'_single_field_edit_preserves_other_values']=Object.keys(base).every(key=>{
      const expected=key===test.edit?changed:base[key];
      return sameValue(saved[key],expected);
    });
    if(test.numeric){
      const extra=['transport','warehouse','security','market_charges','loading_offloading','other_costs'].reduce((sum,key)=>sum+Number(saved[key]),0);
      checks[test.endpoint+'_existing_totals_and_zero_cost_preserved']=Number(saved.security)===0&&Math.abs(Number(saved.total_additional_cost)-extra)<0.000001&&Math.abs(Number(saved.total_estimated_landing_storage_cost)-Number(saved.purchase_price_reference)-extra)<0.000001;
    }
    await page.reload();await id.fill(String(rows[0].id));await waitForField(test.edit,changed,test.numeric);
    checks[test.endpoint+'_reload_preserves_saved_edit']=sameValue(await form.locator('[name='+test.clear+']').inputValue(),base[test.clear]);
    await form.locator('[name='+test.clear+']').fill('');response=page.waitForResponse(response=>response.request().method()==='PATCH'&&new URL(response.url()).pathname==='/api/'+test.endpoint+'/'+rows[0].id);await form.getByRole('button',{name:test.button,exact:true}).click();assert.equal((await response).status(),200);
    const cleared=(await api('/'+test.endpoint+'/'+rows[0].id)).body[test.clear];
    checks[test.endpoint+'_explicit_clearing_remains_possible']=test.numeric?sameValue(cleared,0):cleared===null;
    await field.fill(test.numeric?'999.50':'Synthetic unsaved value');
    await id.fill(String(rows[1].id));await waitForField(test.edit,rows[1][test.edit],test.numeric);
    checks[test.endpoint+'_switching_id_loads_other_record']=sameValue(await form.locator('[name='+test.clear+']').inputValue(),base[test.clear]);
    checks[test.endpoint+'_switch_discards_only_unsaved_changes']=sameValue((await api('/'+test.endpoint+'/'+rows[0].id)).body[test.edit],changed);
    await id.fill('999999');await page.locator('main .status-box.error').filter({hasText:'Record not found. Enter an existing ID or leave it blank to create.'}).waitFor();
    checks[test.endpoint+'_unknown_id_blocks_wrong_record_submit']=await id.evaluate(input=>!input.checkValidity())&&await field.inputValue()===(test.numeric?'0':'');
    await id.fill('');checks[test.endpoint+'_blank_id_restores_creation_defaults']=await field.inputValue()===(test.numeric?'0':'')&&await id.evaluate(input=>input.checkValidity());
    for(const [key,value] of Object.entries(base)){
      const control=form.locator('[name='+key+']');
      if(await control.evaluate(element=>element.tagName==='SELECT'))await control.selectOption(String(value));else await control.fill(String(value));
    }
    response=page.waitForResponse(response=>response.request().method()==='POST'&&new URL(response.url()).pathname==='/api/'+test.endpoint);await form.getByRole('button',{name:test.button,exact:true}).click();const added=await response;assert.equal(added.status(),201);created.push([test.endpoint,(await added.json()).id,test.canDelete!==false]);checks[test.endpoint+'_original_creation_still_works']=true;
  }
  assert.deepEqual((await api('/price-updates/admin/history')).body,prices);assert.equal(outside,0);
  const failures=Object.entries(checks).filter(([,value])=>!value).map(([name])=>name);
  const report={checks,failures,expected_original_bug:expectBug,original_price_history_unchanged:true,disposable_preview_reseed_required:created.some(([, ,canDelete])=>!canDelete),external_page_requests:outside,production_connections:0};fs.writeFileSync(path.join(lab,'runtime/admin-edit-prefill-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(expectBug)assert.ok(failures.length>0);else assert.deepEqual(failures,[]);
} finally {for(const [endpoint,id,canDelete] of created.reverse())if(canDelete)await api('/'+endpoint+'/'+id,'DELETE').catch(()=>{});await browser.close();}
