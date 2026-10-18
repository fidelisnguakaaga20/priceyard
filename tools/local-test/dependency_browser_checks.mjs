import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const recovery=path.resolve(lab,'../../.git/priceyard-local-recovery-20261015/p00/runtime');
const {chromium}=await import(pathToFileURL(path.join(recovery,'npm-tools-309adbe095ff487cb1d6bd447c580c70/node_modules/playwright/index.mjs')));
const old=path.join(lab,'runtime/frontend-7cf451c3d7a54985a699a81d503125d4/dist/assets');
const current=JSON.parse(fs.readFileSync(path.join(lab,'runtime/frontend.json'),'utf8'));
const built=path.join(current.path,'dist/assets');
const css=folder=>fs.readFileSync(path.join(folder,fs.readdirSync(folder).find(name=>name.endsWith('.css'))),'utf8');
const styles=[css(old),css(built)];
const browser=await chromium.launch({headless:true,args:['--disable-background-networking','--disable-component-update','--disable-sync','--no-first-run']});
const context=await browser.newContext({extraHTTPHeaders:{'X-PriceYard-Test-Client':crypto.randomUUID()},serviceWorkers:'block'});
let outside=0;await context.route('**/*',r=>{if(new URL(r.request().url()).origin===origin)return r.continue();outside++;return r.abort();});
await context.addInitScript(()=>localStorage.setItem('priceyard_onboarding_seen','1'));
const page=await context.newPage();page.setDefaultTimeout(12000);
try{
 const viewports=[];
 for(const width of [1366,375]){
  await page.setViewportSize({width,height:900});await page.goto(origin+'/prices');await page.locator('.price-card').first().waitFor();
  const signatures=[];
  for(const text of styles){
   signatures.push(await page.evaluate(async text=>{
    document.querySelectorAll('link[rel=stylesheet]').forEach(link=>link.disabled=true);document.querySelector('#synthetic-css-comparison')?.remove();
    const style=document.createElement('style');style.id='synthetic-css-comparison';style.textContent=text+'\n*{animation:none!important;transition:none!important}';document.head.append(style);
    await new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(resolve)));
    return {overflow:document.documentElement.scrollWidth>innerWidth,elements:[...document.querySelectorAll('header,nav,main h1,.price-card,.price-range,.filter-bar,.button')].slice(0,40).map(node=>{
     const box=node.getBoundingClientRect(),style=getComputedStyle(node);return {tag:node.tagName,width:Math.round(box.width*10)/10,height:Math.round(box.height*10)/10,color:style.color,background:style.backgroundColor,font:style.font,fontWeight:style.fontWeight,padding:style.padding,border:style.border,display:style.display};
    })};
   },text));
  }
  assert.deepEqual(signatures[1],signatures[0]);viewports.push(width);
 }
 await page.goto(origin+'/commodities/Egusi?commodity_id=1');await page.getByRole('heading',{name:'Egusi',exact:true}).first().waitFor();await page.locator('.price-card-note').first().waitFor();
 assert.equal(await page.getByText(/Grade:|Grade not recorded/).count(),0);assert.equal(outside,0);
 const report={upgraded_compiler_css_format_differs:styles[0]!==styles[1],same_computed_original_layout_and_typography:true,viewports,existing_id_deep_link_and_original_price_card:true,external_requests:outside,production_connections:0};
 fs.writeFileSync(path.join(lab,'runtime/dependency-browser-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
}finally{await browser.close();}
