import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const before=process.argv.includes('--expect-bug');
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block',viewport:{width:1366,height:900}});
let outside=0,temporaryId;
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
async function api(url,method='GET',body) {
  return page.evaluate(async({url,method,body})=>{
    const response=await fetch('/api'+url,{method,headers:{Authorization:'Bearer '+localStorage.getItem('priceyard_access_token'),'Content-Type':'application/json'},...(body?{body:JSON.stringify(body)}:{})});
    return {status:response.status,body:response.status===204?null:await response.json()};
  },{url,method,body});
}
const checks={};
async function selection(element,input,id,prefix) {
  checks[prefix+'_tab_stop']=await element.evaluate(node=>node.tabIndex===0);
  for(const [key,suffix] of [['Enter','enter'],['Space','space']]) {
    await input.fill('');await input.blur();
    await page.keyboard.press('Tab');await element.focus();
    const focused=await element.evaluate(node=>document.activeElement===node);
    await page.keyboard.press(key);
    checks[prefix+'_'+suffix]=focused&&await input.inputValue()===String(id);
  }
  checks[prefix+'_visible_focus']=await element.evaluate(node=>node.matches(':focus-visible')&&getComputedStyle(node).outlineStyle!=='none'&&parseFloat(getComputedStyle(node).outlineWidth)>=2);
  await input.fill('');await element.click();
  checks[prefix+'_mouse_selection_preserved']=await input.inputValue()===String(id);
}
try {
  await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('admin@example.com');await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Admin',exact:true}).waitFor();
  const historyBefore=(await api('/price-updates/admin/history')).body;
  const draft=await api('/faq','POST',{question:'Synthetic keyboard draft',answer:'Synthetic local keyboard check',category:'Local testing'});assert.equal(draft.status,201);temporaryId=draft.body.id;
  let writes=0;page.on('request',request=>{if(request.url().startsWith(origin+'/api/')&&request.method()!=='GET')writes++;});
  await page.goto(origin+'/admin/prices');const row=page.locator('tbody tr').first();await row.waitFor();const priceId=await row.locator('td').first().innerText();
  await selection(row,page.getByLabel('Record ID',{exact:true}),priceId,'price_row');
  await page.goto(origin+'/admin/faq');const published=page.locator('article').filter({has:page.getByRole('heading',{name:'Local testing question',exact:true})});await published.waitFor();
  const publishedId=(await published.locator('.eyebrow').innerText()).match(/^#(\d+)/)[1];
  await selection(published,page.getByLabel('FAQ ID',{exact:true}),publishedId,'published_faq');
  const hidden=page.locator('article').filter({has:page.getByRole('heading',{name:'Synthetic keyboard draft',exact:true})});await hidden.waitFor();
  await selection(hidden,page.getByLabel('FAQ ID',{exact:true}),temporaryId,'hidden_faq');
  await page.goto(origin+'/admin/users');await page.locator('.admin-table-view tbody tr').first().waitFor();
  checks.desktop_role_names=await page.locator('.admin-table-view select').evaluateAll(nodes=>nodes.every(node=>node.getAttribute('aria-label')?.startsWith('Role for ')&&node.getAttribute('aria-label')?.includes('@example.com')));
  await page.setViewportSize({width:375,height:812});
  checks.mobile_role_names=await page.locator('.admin-mobile-list select').evaluateAll(nodes=>nodes.length>0&&nodes.every(node=>node.getAttribute('aria-label')?.startsWith('Role for ')));
  await page.goto(origin+'/admin/subscriptions');await page.locator('tbody tr').first().waitFor();
  checks.subscription_status_names=await page.locator('tbody select').evaluateAll(nodes=>nodes.length>0&&nodes.every(node=>node.getAttribute('aria-label')?.startsWith('Subscription status for user #')));
  checks.selection_does_not_save_or_publish=writes===0;
  checks.history_unchanged=JSON.stringify((await api('/price-updates/admin/history')).body)===JSON.stringify(historyBefore);
  const report={before,checks,failures:Object.entries(checks).filter(([,pass])=>!pass).map(([name])=>name),external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/keyboard-checks'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
  if(!before)assert.equal(report.failures.length,0);assert.equal(outside,0);
} finally {if(temporaryId)assert.equal((await api('/faq/'+temporaryId,'DELETE')).status,204);await browser.close();}
