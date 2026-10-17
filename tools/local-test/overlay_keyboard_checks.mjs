import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const before=process.argv.includes('--expect-bug'),checks={};let outside=0;
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
async function fixture(seen=true){
  const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block',viewport:{width:375,height:812}});
  await context.route('**/*',route=>{if(new URL(route.request().url()).origin===origin)return route.continue();outside++;return route.abort();});
  if(seen)await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
  const page=await context.newPage();page.setDefaultTimeout(15000);await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();return {context,page};
}
try {
  const {context,page}=await fixture();
  const trigger=page.getByRole('button',{name:'What does confidence mean?',exact:true});
  await trigger.focus();await page.keyboard.press('Enter');const popup=page.locator('.confidence-info-popover');await popup.waitFor();
  const controlled=await trigger.getAttribute('aria-controls');checks.confidence_help_relationship=!!controlled&&await popup.getAttribute('id')===controlled;
  await page.keyboard.press('Tab');checks.help_close_reachable_by_tab=await popup.getByRole('button',{name:'Close',exact:true}).evaluate(node=>node===document.activeElement);
  await page.keyboard.press('Escape');checks.help_escape_closes=await popup.count()===0;checks.help_escape_restores_trigger=await trigger.evaluate(node=>node===document.activeElement);
  if(await popup.count())await popup.getByRole('button',{name:'Close',exact:true}).click();
  await trigger.focus();await page.keyboard.press('Space');await popup.waitFor();await popup.getByRole('button',{name:'Close',exact:true}).click();checks.original_help_close_restores_trigger=await trigger.evaluate(node=>node===document.activeElement);
  const menu=page.getByRole('button',{name:'Toggle navigation',exact:true});await menu.focus();await page.keyboard.press('Enter');const nav=page.getByRole('navigation',{name:'Primary navigation',exact:true});await nav.waitFor();
  checks.menu_controls_existing_navigation=await menu.getAttribute('aria-controls')===await nav.getAttribute('id')&&!!await nav.getAttribute('id');
  await page.keyboard.press('Tab');checks.menu_links_reachable=await nav.getByRole('link',{name:'Current Prices',exact:true}).evaluate(node=>node===document.activeElement);
  await page.keyboard.press('Escape');checks.menu_escape_closes=await menu.getAttribute('aria-expanded')==='false';checks.menu_escape_restores_toggle=await menu.evaluate(node=>node===document.activeElement);
  await context.close();
  const tour=await fixture(false);const dialog=tour.page.getByRole('dialog',{name:'Welcome to PriceYard',exact:true});await dialog.waitFor();
  const skip=dialog.getByRole('button',{name:'Skip',exact:true}),next=dialog.getByRole('button',{name:'Next',exact:true});
  checks.tour_initial_focus_inside=await dialog.evaluate(node=>node.contains(document.activeElement));
  await skip.focus();await tour.page.keyboard.press('Shift+Tab');checks.tour_reverse_tab_contained=await next.evaluate(node=>node===document.activeElement);
  await next.focus();await tour.page.keyboard.press('Tab');checks.tour_forward_tab_contained=await skip.evaluate(node=>node===document.activeElement);
  await next.focus();await tour.page.keyboard.press('Enter');await dialog.getByText('Welcome to PriceYard (2/4)',{exact:true}).waitFor();
  await dialog.getByRole('button',{name:'Back',exact:true}).press('Enter');await dialog.getByText('Welcome to PriceYard (1/4)',{exact:true}).waitFor();checks.original_tour_next_and_back_preserved=true;
  await skip.focus();await tour.page.keyboard.press('Escape');checks.tour_escape_uses_existing_skip=await dialog.count()===0;
  if(await dialog.count())await skip.click();
  checks.tour_original_seen_policy_preserved=await tour.page.evaluate(()=>localStorage.getItem('priceyard_onboarding_seen')==='1');
  checks.tour_restores_focus_after_dismissal=await tour.page.locator('.brand').evaluate(node=>node===document.activeElement);
  await tour.context.close();
  const report={before,checks,failures:Object.entries(checks).filter(([,pass])=>!pass).map(([key])=>key),external_page_requests:outside,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/overlay-keyboard'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));if(!before)assert.equal(report.failures.length,0);assert.equal(outside,0);
} finally {await browser.close();}
