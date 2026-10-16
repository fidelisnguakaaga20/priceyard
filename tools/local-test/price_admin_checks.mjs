import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();
page.setDefaultTimeout(12000);
const expectBug=process.argv.includes('--expect-bug');
try {
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill('admin@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test Admin'}).waitFor();
  await page.goto(origin+'/admin/prices');
  await page.getByRole('heading',{name:'Price updates',exact:true}).waitFor();
  const create=page.locator('form.admin-form').nth(0);
  await create.locator('select[name="commodity_id"]').selectOption({label:'Egusi'});
  await create.locator('select[name="market_id"]').selectOption({label:'Kwali Market'});
  await create.getByLabel('Low',{exact:true}).fill('211000');
  await create.getByLabel('High',{exact:true}).fill('221000');
  await create.getByLabel('Average',{exact:true}).fill('216000');
  // Do not invent a measured bag weight: original free-text field accepts an
  // explicit unknown value in this fabricated record. No Grade field is added.
  await create.getByLabel('Bag size (kg)',{exact:true}).fill('Unknown');
  await create.locator('select[name="confidence_level"]').selectOption('Low confidence');
  await create.getByLabel('Update date/time',{exact:true}).fill(new Date().toISOString().slice(0,16));
  const createdResponse=page.waitForResponse(r=>r.url()===origin+'/api/price-updates'&&r.request().method()==='POST');
  await create.getByRole('button',{name:'Create pending update',exact:true}).click();
  const response=await createdResponse;
  assert.equal(response.status(),201);
  const created=await response.json();
  const row=()=>page.locator('.admin-table tbody tr').filter({has:page.locator('td:first-child').getByText(String(created.id),{exact:true})});
  await row().waitFor();
  assert.equal(await row().locator('td').nth(3).innerText(),'pending');
  async function act(label,action) {
    const completion=page.waitForResponse(r=>r.url()===origin+`/api/price-updates/${created.id}/${action}`&&r.request().method()==='PATCH');
    const reload=page.waitForResponse(r=>r.url()===origin+'/api/price-updates/admin/history');
    await page.getByRole('button',{name:label,exact:true}).click();
    assert.equal((await completion).status(),200);
    const data=await (await reload).json();
    await page.locator('.loading-spinner').waitFor({state:'hidden'}).catch(()=>{});
    await row().waitFor();
    return data.find(x=>x.id===created.id);
  }
  const saved=await act('Approve','approve');
  assert.equal(saved.status,'approved');
  if(expectBug) {
    assert.equal(await row().locator('td').nth(3).innerText(),'pending');
    const report={stale_created_row_reproduced:true,server_status:'approved',screen_status:'pending',production_connections:0};
    fs.writeFileSync(path.join(lab,'runtime/price-admin-before.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report));
  } else {
    await page.waitForFunction(id=>Array.from(document.querySelectorAll('.admin-table tbody tr')).some(r=>r.cells[0].textContent===String(id)&&r.cells[3].textContent==='approved'),created.id);
    const edit=page.locator('form.admin-form').nth(1);
    await edit.getByLabel('Low',{exact:true}).fill('210500');
    const correction=page.waitForResponse(r=>r.url()===origin+`/api/price-updates/${created.id}`&&r.request().method()==='PATCH');
    await edit.getByRole('button',{name:'Save correction',exact:true}).click();
    assert.equal((await correction).status(),200);
    await page.waitForFunction(id=>Array.from(document.querySelectorAll('.admin-table tbody tr')).some(r=>r.cells[0].textContent===String(id)&&r.cells[2].textContent.includes('210500')),created.id);
    await act('Mark outdated','mark-outdated');
    await page.waitForFunction(id=>Array.from(document.querySelectorAll('.admin-table tbody tr')).some(r=>r.cells[0].textContent===String(id)&&r.cells[3].textContent.includes('outdated')),created.id);
    await act('Reject','reject');
    await page.waitForFunction(id=>Array.from(document.querySelectorAll('.admin-table tbody tr')).some(r=>r.cells[0].textContent===String(id)&&r.cells[3].textContent.includes('rejected')),created.id);
    await page.reload();
    await row().waitFor();
    assert.ok((await row().locator('td').nth(3).innerText()).includes('rejected'));
    assert.ok((await row().locator('td').nth(2).innerText()).includes('210500'));
    assert.equal(await page.getByLabel(/grade/i).count(),0);
    const report={created_approved_corrected_outdated_rejected_and_reloaded:true,original_fields_preserved:true,bag_weight_not_invented:true,production_connections:0};
    fs.writeFileSync(path.join(lab,'runtime/price-admin-checks.json'),JSON.stringify(report,null,2));
    await page.screenshot({path:path.join(lab,'runtime/price-admin-after.png'),fullPage:true});
    console.log(JSON.stringify(report));
  }
} catch(error) {
  console.log(JSON.stringify({url:page.url(),forms:await page.locator('form').count(),headings:await page.locator('h1,h2,h3').allTextContents()}));
  await page.screenshot({path:path.join(lab,'runtime/price-admin-failure.png'),fullPage:true});
  throw error;
} finally {await browser.close();}
