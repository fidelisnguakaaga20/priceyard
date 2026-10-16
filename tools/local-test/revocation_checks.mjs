import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const origin='http://127.0.0.1:55446';
const result={};
async function makePage(){
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
  await context.route('**/*',route=>new URL(route.request().url()).origin===origin?route.continue():route.abort());
  await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  const page=await context.newPage();page.setDefaultTimeout(12000);
  return {context,page};
}
async function login(page,email,password='PriceYardDemo8!'){
  await page.goto(origin+'/login');
  await page.getByLabel('Email',{exact:true}).fill(email);
  await page.getByLabel('Password',{exact:true}).fill(password);
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  await page.getByRole('heading',{name:/^Welcome, Test /}).waitFor();
  return page.evaluate(()=>localStorage.getItem('priceyard_access_token'));
}
try{
  {
    const {context,page}=await makePage();
    const token=await login(page,'free@example.com');
    const confirmation=page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/logout'&&response.status()===204);
    await page.getByRole('button',{name:'Log out',exact:true}).click();
    await confirmation;
    const status=await page.evaluate(async token=>(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status,token);
    assert.equal(status,401);
    assert.equal(await page.evaluate(()=>localStorage.getItem('priceyard_access_token')),null);
    result.existing_logout_button_revokes_server_credential=true;
    await context.close();
  }
  {
    const old=await makePage();
    const oldToken=await login(old.page,'reset@example.com');
    const reset=await makePage();
    await reset.page.goto(origin+'/forgot-password');
    await reset.page.getByLabel('Email',{exact:true}).fill('reset@example.com');
    await reset.page.getByRole('button',{name:'Send reset link',exact:true}).click();
    await reset.page.locator('.status-box.success').waitFor();
    await reset.page.goto(origin+'/__test__/inbox');
    await reset.page.getByRole('link',{name:'Open reset link for reset@example.com',exact:true}).last().click();
    await reset.page.getByRole('heading',{name:'Create a new password',exact:true}).waitFor();
    const resetUrl=reset.page.url();
    await reset.page.getByLabel('New password',{exact:true}).fill('UpdatedPassword8!');
    await reset.page.getByLabel('Confirm new password',{exact:true}).fill('UpdatedPassword8!');
    await reset.page.getByRole('button',{name:'Reset password',exact:true}).click();
    await reset.page.getByRole('heading',{name:'Password updated',exact:true}).waitFor();
    const rejected=await reset.page.evaluate(async token=>(await fetch('/api/auth/me',{headers:{Authorization:'Bearer '+token}})).status,oldToken);
    assert.equal(rejected,401);
    await old.page.reload();
    await old.page.getByRole('heading',{name:'Log in to PriceYard',exact:true}).waitFor();
    await login(reset.page,'reset@example.com','UpdatedPassword8!');
    await reset.page.goto(resetUrl);
    await reset.page.getByLabel('New password',{exact:true}).fill('AnotherPassword8!');
    await reset.page.getByLabel('Confirm new password',{exact:true}).fill('AnotherPassword8!');
    const retry=reset.page.waitForResponse(response=>new URL(response.url()).pathname==='/api/auth/reset-password');
    await reset.page.getByRole('button',{name:'Reset password',exact:true}).click();
    assert.equal((await retry).status(),400);
    result.original_reset_form_and_local_inbox=true;
    result.password_reset_revokes_existing_login=true;
    result.new_password_login_and_single_use_link=true;
    await old.context.close();await reset.context.close();
  }
  const report={result,production_connections:0,live_emails_sent:0};
  fs.writeFileSync(path.join(lab,'runtime/revocation-checks.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
}finally{await browser.close()}
