// Published Paystack TEST details only. Never use an owner's card or live URL.
import fs from 'node:fs';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(lab,'../..');
const run=path.join(lab,'runtime/provider-tunnel-20261020');
const status=JSON.parse(fs.readFileSync(path.join(run,'remaining-result.json'),'utf8'));
const checkout=JSON.parse(fs.readFileSync(path.join(run,'remaining-checkout.json'),'utf8'));
if(status.status!=='awaiting_approved_TEST_checkout_and_Google_consent'||!status.TEST_webhook_change_owner_confirmed||new URL(checkout.authorization_url).hostname!=='checkout.paystack.com')throw Error('Unapproved checkout state');
const {chromium}=await import(pathToFileURL(path.join(root,'.git/priceyard-local-recovery-20261015/p00/runtime/npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
let browser;
const result={mode:'inspection_only',TEST_mode_visible:false};
try{
  browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
  const context=await browser.newContext({serviceWorkers:'block'});
  await context.route('**/*',route=>{
    const host=new URL(route.request().url()).hostname;
    if(host.endsWith('.supabase.co')||host.endsWith('.onrender.com'))return route.abort();
    if(host.endsWith('.trycloudflare.com')&&host!==new URL(status.public_origin).hostname)return route.abort();
    return route.continue();
  });
  const page=await context.newPage();page.setDefaultTimeout(10000);
  await page.goto(checkout.authorization_url,{waitUntil:'domcontentloaded',timeout:25000});
  await page.waitForTimeout(2000);
  result.TEST_mode_visible=/test mode|test payment|test card/i.test(await page.locator('body').innerText());
  result.human_verification_required=await page.locator('input[name="cf-turnstile-response"]').count()>0;
  result.frames=[];
  for(const frame of page.frames()){
    let host='';try{host=new URL(frame.url()).hostname;}catch{}
    result.frames.push({host,inputs:await frame.locator('input').evaluateAll(nodes=>nodes.map(n=>({type:n.type,placeholder:n.placeholder,name:n.name,id:n.id}))),buttons:await frame.getByRole('button').allTextContents()});
  }
  await context.close();
}catch(error){result.error_type=error.name;}
finally{if(browser)await browser.close();}
fs.writeFileSync(path.join(run,'remaining-checkout-browser.json'),JSON.stringify(result,null,2));
process.stdout.write(JSON.stringify(result));
