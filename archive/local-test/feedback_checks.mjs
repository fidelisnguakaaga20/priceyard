import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446',expectBug=process.argv.includes('--expect-bug'),checks={};let outside=0;
const png='iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII=';
async function fixture(){
 const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
 await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
 await context.addInitScript(({png})=>{
  localStorage.setItem('priceyard_onboarding_seen','1');
  const Reader=window.FileReader;
  window.FileReader=class extends Reader{
   readAsDataURL(file){
    if(file.name!=='slow.png')return super.readAsDataURL(file);
    window.__finishSlow=()=>{Object.defineProperty(this,'result',{value:'data:image/png;base64,'+png});this.onload(new ProgressEvent('load'));};
   }
  };
 },{png});
 const page=await context.newPage();page.setDefaultTimeout(15000);
 await page.goto(origin+'/login');await page.getByLabel('Email',{exact:true}).fill('trial@example.com');
 await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');await page.getByRole('button',{name:'Log in',exact:true}).click();
 await page.waitForURL('**/dashboard');await page.getByRole('heading',{name:'Welcome, Test Trial',exact:true}).waitFor();
 await page.goto(origin+'/feedback');await page.getByRole('heading',{name:'Rate your PriceYard experience'}).waitFor();
 return {context,page,input:page.locator('input[type=file]')};
}
async function settle(page){await page.evaluate(()=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve))));}
try{
 {
  const {context,page,input}=await fixture();
  await input.setInputFiles({name:'valid.png',mimeType:'image/png',buffer:Buffer.from(png,'base64')});
  await page.getByText(/valid.png attached/).waitFor();
  await input.setInputFiles({name:'oversized.png',mimeType:'image/png',buffer:Buffer.alloc(2*1024*1024+1)});
  await page.locator('.status-box.error').getByText('Screenshot must be smaller than 2MB.').waitFor();
  checks.invalid_replacement_clears_previous_attachment=await page.getByText(/valid.png attached/).count()===0;
  await page.locator('select').selectOption('true');
  const responsePromise=page.waitForResponse(r=>r.url()===origin+'/api/feedback'&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Submit feedback',exact:true}).click();const response=await responsePromise;
  assert.equal(response.status(),201);const saved=await response.json();
  checks.invalid_replacement_is_not_submitted= saved.screenshot_data===null;
  await page.locator('.status-box.success').getByText('Thank you. Your feedback was submitted.').waitFor();
  checks.original_form_still_saves=true;
  await context.close();
 }
 {
  const {context,page,input}=await fixture();
  await input.setInputFiles({name:'slow.png',mimeType:'image/png',buffer:Buffer.from(png,'base64')});
  await page.waitForFunction(()=>typeof window.__finishSlow==='function');
  await input.setInputFiles({name:'new.png',mimeType:'image/png',buffer:Buffer.from(png,'base64')});
  await page.getByText(/new.png attached/).waitFor();await page.evaluate(()=>window.__finishSlow());await settle(page);
  checks.last_selected_file_wins=await page.getByText(/new.png attached/).count()===1;
  await context.close();
 }
 assert.equal(outside,0);
 for(const [name,value] of Object.entries(checks))assert.equal(value,name==='original_form_still_saves'?true:!expectBug,name);
 const report={checks,expected_original_bug:expectBug,external_page_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/feedback-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
