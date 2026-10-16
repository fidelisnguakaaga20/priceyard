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
const question='Fabricated hidden FAQ '+crypto.randomUUID();
const expectBug=process.argv.includes('--expect-bug');
try {
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill('admin@example.com');
  await page.getByLabel('Password',{exact:true}).fill('PriceYardDemo8!');
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:'Welcome, Test Admin'}).waitFor();
  await page.goto(origin+'/admin/faq');
  const form=page.locator('form.admin-form').first();
  await form.getByLabel('Question',{exact:true}).fill(question);
  await form.getByLabel('Answer',{exact:true}).fill('Fabricated local answer only.');
  await form.getByLabel('Category',{exact:true}).fill('Local testing');
  const creation=page.waitForResponse(r=>r.url()===origin+'/api/faq'&&r.request().method()==='POST');
  await form.getByRole('button',{name:'Create hidden FAQ',exact:true}).click();
  const response=await creation;
  assert.equal(response.status(),201);
  const item=await response.json();
  await page.getByRole('heading',{name:question,exact:true}).waitFor();
  async function publicView() {
    return page.evaluate(async id=>({list:await fetch('/api/faq').then(r=>r.json()),detail:(await fetch('/api/faq/'+id)).status}),item.id);
  }
  assert.equal((await publicView()).detail,404);
  await page.reload();
  await page.getByRole('heading',{name:'FAQ',exact:true}).waitFor();
  if(expectBug) {
    await page.getByRole('heading',{name:'Local testing question',exact:true}).waitFor();
    assert.equal(await page.getByRole('heading',{name:question,exact:true}).count(),0);
    const report={hidden_draft_lost_from_admin_after_reload:true,public_hidden_detail:404,production_connections:0};
    fs.writeFileSync(path.join(lab,'runtime/faq-before.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report));
  } else {
    await page.getByRole('heading',{name:question,exact:true}).waitFor();
    await page.getByLabel('FAQ ID',{exact:true}).fill(String(item.id));
    async function action(label,kind) {
      const response=page.waitForResponse(r=>r.url()===origin+`/api/faq/${item.id}/${kind}`&&r.request().method()==='PATCH');
      await page.getByRole('button',{name:label,exact:true}).click();
      assert.equal((await response).status(),200);
      await page.getByRole('button',{name:label,exact:true}).waitFor({state:'visible'});
      await page.waitForFunction(()=>!document.querySelector('button:disabled'));
    }
    await action('Publish','publish');
    assert.equal((await publicView()).detail,200);
    await page.reload();
    await page.getByRole('heading',{name:question,exact:true}).waitFor();
    await page.getByLabel('FAQ ID',{exact:true}).fill(String(item.id));
    await action('Hide','hide');
    assert.equal((await publicView()).detail,404);
    await page.reload();
    await page.getByRole('heading',{name:question,exact:true}).waitFor();
    await page.getByLabel('FAQ ID',{exact:true}).fill(String(item.id));
    const deletion=page.waitForResponse(r=>r.url()===origin+`/api/faq/${item.id}`&&r.request().method()==='DELETE');
    await page.getByRole('button',{name:'Delete',exact:true}).click();
    assert.equal((await deletion).status(),204);
    await page.waitForFunction(text=>!Array.from(document.querySelectorAll('h3')).some(x=>x.textContent===text),question);
    const report={hidden_draft_survives_reload:true,publish_hide_public_boundary:true,deleted_fake_draft_disappears:true,production_connections:0};
    fs.writeFileSync(path.join(lab,'runtime/faq-checks.json'),JSON.stringify(report,null,2));
    console.log(JSON.stringify(report));
  }
}finally{await browser.close();}
