import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const before=process.argv.includes('--expect-bug'),checks={};let outside=0;
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(15000);
try {
  for(const [screen,ids,minimum] of [['/login',['login-password'],1],['/register',['register-password'],8],['/reset-password?token=synthetic-input-check-token-0123456789',['reset-password','confirm-reset-password'],8]]) {
    await page.goto(origin+screen);
    for(const id of ids) {
      const input=page.locator('#'+id);await input.waitFor();
      for(const [value,name,valid] of [['好'.repeat(25),'rejects_overlong_utf8',false],['😀'.repeat(19),'rejects_overlong_emoji',false],['好'.repeat(24),'accepts_exact_byte_limit',true],['x'.repeat(72),'accepts_ascii_limit',true],['😀'.repeat(4),'existing_character_minimum',minimum===1]]) {
        await input.fill(value);checks[id+'_'+name]=await input.evaluate(node=>node.checkValidity())===valid;
        assert.equal(await input.inputValue(),value,'Input must never silently alter the typed password');
      }
      await input.fill('😀'.repeat(8));checks[id+'_eight_unicode_characters_accepted']=await input.evaluate(node=>node.checkValidity());
      const toggle=input.locator('..').getByRole('button');await toggle.click();
      checks[id+'_visibility_keeps_value_and_validity']=await input.getAttribute('type')==='text'&&await input.inputValue()==='😀'.repeat(8)&&await input.evaluate(node=>node.checkValidity());
      await toggle.click();
      await input.fill('x');checks[id+'_existing_short_password_rule']=await input.evaluate(node=>node.checkValidity())===(minimum===1);
    }
  }
  const report={before,checks,failures:Object.entries(checks).filter(([,pass])=>!pass).map(([key])=>key),typed_passwords_not_truncated:true,no_account_or_subscription_changes:true,external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/password-input'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!before)assert.equal(report.failures.length,0);assert.equal(outside,0);
} finally {await browser.close();}
