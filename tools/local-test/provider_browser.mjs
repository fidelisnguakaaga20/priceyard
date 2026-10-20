// One browser, synthetic identity only; no Google password or real card input.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL, fileURLToPath} from 'node:url';
const input=JSON.parse(fs.readFileSync(0,'utf8'));
const lab=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(lab,'../..');
const {chromium}=await import(pathToFileURL(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const result={original_login_browser:'not_verified',google_origin_rejected:false,google_interactive_login:'not_attempted',test_checkout_inspected_without_payment:false};
try {
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.route('**/*',route=>{
    const host=new URL(route.request().url()).hostname;
    if(host.endsWith('.supabase.co')||host.endsWith('.onrender.com'))return route.abort();
    return route.continue();
  });
  const page=await context.newPage();page.setDefaultTimeout(12000);
  page.on('console',message=>{if(/origin.*not allowed|origin.*not.*authorized/i.test(message.text()))result.google_origin_rejected=true;});
  await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  await page.goto(input.origin+'/?ticket='+encodeURIComponent(input.gate));
  await page.getByLabel('Email',{exact:true}).fill(input.email);
  await page.getByLabel('Password',{exact:true}).fill(input.password);
  await page.getByRole('button',{name:'Log in',exact:true}).click();
  await page.waitForURL('**/dashboard');
  const cookie=(await context.cookies()).find(c=>c.name==='__Host-priceyard_session');
  if(!cookie?.secure||!cookie.httpOnly||cookie.sameSite!=='Lax')throw Error('Cookie flags');
  const secret=await page.evaluate(()=>localStorage.getItem('priceyard_access_token')||sessionStorage.getItem('priceyard_access_token'));
  if(secret)throw Error('Browser login secret is script-readable');
  result.original_login_browser='passed';
  if(input.checkout_url){
    if(new URL(input.checkout_url).hostname!=='checkout.paystack.com')throw Error('Checkout host');
    const checkout=await context.newPage();
    await checkout.goto(input.checkout_url,{waitUntil:'domcontentloaded',timeout:25000});
    await checkout.waitForTimeout(2000);
    result.test_checkout_inspected_without_payment=true;
    result.test_mode_visible=/test mode|test payment|test card/i.test(await checkout.locator('body').innerText());
    await checkout.close();
  }
  await context.close();
} catch(error){result.failure_type=error.name;}
finally{await browser.close();}
process.stdout.write(JSON.stringify(result));
