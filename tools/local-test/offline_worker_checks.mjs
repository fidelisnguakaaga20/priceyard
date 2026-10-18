// Execute the actual worker source with in-memory caches and a fake fetch.
// This VM has no native network, credentials, service workers or provider clients.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),origin='http://127.0.0.1:55446';
const source=fs.readFileSync(path.join(lab,'../../frontend/public/sw.js'),'utf8');
const before=process.argv.includes('--expect-bug'),savedAt='2026-10-17T12:00:00.000Z';
const tests=[];
function fixture(api=origin+'/api') {
  const listeners=new Map(),stores=new Map(),requests=[];
  let available=true,reply=()=>new Response(JSON.stringify({price_low:'210000',update_date_time:'2026-10-16T10:00:00Z'}),{headers:{'Content-Type':'application/json'}}),writesFail=false;
  const key=request=>new URL(typeof request==='string'?request:request.url,origin).href;
  const fakeFetch=async request=>{requests.push(key(request));if(!available)throw new Error('Synthetic network unavailable');return reply();};
  const caches={keys:async()=>[...stores.keys()],delete:async name=>stores.delete(name),open:async name=>{
    if(!stores.has(name))stores.set(name,new Map());const store=stores.get(name);
    return {match:async request=>store.get(key(request))?.clone(),put:async(request,response)=>{if(writesFail)throw new Error('Synthetic quota failure');store.set(key(request),response.clone());},delete:async request=>store.delete(key(request)),addAll:async paths=>{for(const entry of paths)store.set(key(entry),(await fakeFetch(entry)).clone());}};
  },match:async request=>{for(const store of stores.values()){const value=store.get(key(request));if(value)return value.clone();}}};
  class FixedDate extends Date {constructor(...args){super(...(args.length?args:[savedAt]));}static now(){return Date.parse(savedAt);}}
  const self={location:new URL(origin+'/sw.js?api='+encodeURIComponent(api)),addEventListener:(kind,callback)=>listeners.set(kind,callback),skipWaiting:()=>{},clients:{claim:async()=>{}}};
  vm.runInNewContext(source,{self,caches,fetch:fakeFetch,URL,Headers,Response,Request,Date:FixedDate,Promise,Error,Set}, {timeout:1000});
  return {stores,requests,caches,setOffline:()=>available=false,setReply:value=>reply=value,failWrites:()=>writesFail=true,
    async event(kind){const waits=[];listeners.get(kind)({waitUntil:promise=>waits.push(promise)});await Promise.all(waits);},
    async fetch(url,{authorization=false,mode='cors',method='GET'}={}){
      const request={url:new URL(url,origin).href,method,mode,headers:new Headers(authorization?{Authorization:'Bearer SYNTHETIC'}:{})};
      let result,intercepted=false;const waits=[];
      listeners.get('fetch')({request,respondWith:promise=>{intercepted=true;result=promise;},waitUntil:promise=>waits.push(promise)});
      const response=await(intercepted?result:fakeFetch(request));await Promise.all(waits);return {response,intercepted};
    }};
}
function test(name,run){tests.push([name,run]);}
test('public current fallback has truthful device time and unchanged record time',async()=>{
  const lab=fixture();const fresh=await lab.fetch('/api/price-updates');assert.equal(fresh.response.headers.get('X-PriceYard-Cache'),null);
  const original=await fresh.response.json();lab.setOffline();const fallback=(await lab.fetch('/api/price-updates')).response;
  assert.equal(fallback.headers.get('X-PriceYard-Cache'),'saved');assert.equal(fallback.headers.get('X-PriceYard-Saved-At'),savedAt);assert.deepEqual(await fallback.json(),original);
});
test('configured separate API origin retains public-only offline functionality',async()=>{
  const lab=fixture('https://synthetic-api.invalid/v1');await lab.fetch('https://synthetic-api.invalid/v1/price-updates');lab.setOffline();assert.equal((await lab.fetch('https://synthetic-api.invalid/v1/price-updates')).response.headers.get('X-PriceYard-Cache'),'saved');
});
for(const endpoint of ['/api/auth/me','/api/payments','/api/users','/api/audit-logs','/api/subscriptions','/api/price-updates/history','/api/price-updates?date=2026-10-16','/api/price-updates/admin/history','/api/quality-signals','/api/faq/admin','/api/market-signals'])test('never intercept private or historical path '+endpoint,async()=>{assert.equal((await fixture().fetch(endpoint)).intercepted,false);});
for(const endpoint of ['/api/price-updates','/assets/synthetic.js','/prices'])test('authorization bypasses every cache branch '+endpoint,async()=>{assert.equal((await fixture().fetch(endpoint,{authorization:true,mode:endpoint==='/prices'?'navigate':'cors'})).intercepted,false);});
for(const endpoint of ['https://outside.invalid/assets/test.js','https://outside.invalid/price-updates','https://outside.invalid/prices'])test('unconfigured origins never enter cache '+endpoint,async()=>{assert.equal((await fixture().fetch(endpoint,{mode:endpoint.endsWith('/prices')?'navigate':'cors'})).intercepted,false);});
test('non-GET writes bypass cache',async()=>{assert.equal((await fixture().fetch('/api/price-updates',{method:'POST'})).intercepted,false);});
test('public filtered list retains its own URL key',async()=>{const lab=fixture();await lab.fetch('/api/price-updates?commodity=Egusi&market=Kwali');lab.setOffline();assert.equal((await lab.fetch('/api/price-updates?commodity=Egusi&market=Kwali')).response.headers.get('X-PriceYard-Cache'),'saved');await assert.rejects(()=>lab.fetch('/api/price-updates?commodity=Another'));});

test('exact existing IDs retain separate public current copies',async()=>{const lab=fixture(),url='/api/price-updates?commodity_id=1&market_id=2';await lab.fetch(url);lab.setOffline();assert.equal((await lab.fetch(url)).response.headers.get('X-PriceYard-Cache'),'saved');await assert.rejects(()=>lab.fetch('/api/price-updates?commodity_id=1&market_id=3'));});
test('commodity identity navigation remains public without widening private query caching',async()=>{assert.equal((await fixture().fetch('/commodities/Egusi?commodity_id=1',{mode:'navigate'})).intercepted,true);for(const url of ['/commodities/Egusi?commodity_id=1&token=synthetic','/prices?commodity_id=1','/api/price-updates?commodity_id=1&date=2026-10-16'])assert.equal((await fixture().fetch(url,{mode:url.startsWith('/api/')?'cors':'navigate'})).intercepted,false);});
test('unmarked or invalid-time copies cannot be replayed',async()=>{for(const stamp of [null,'invalid']){const lab=fixture(),cache=await lab.caches.open('priceyard-v2-data');await cache.put('/api/price-updates',new Response('{}',{headers:stamp?{'X-PriceYard-Saved-At':stamp}:{}}));lab.setOffline();await assert.rejects(()=>lab.fetch('/api/price-updates'));}});
test('unrelated old caches are never used for fallback',async()=>{const lab=fixture(),cache=await lab.caches.open('unrelated');await cache.put('/api/price-updates',new Response('{}'));lab.setOffline();await assert.rejects(()=>lab.fetch('/api/price-updates'));});
test('activation removes only the two known legacy PriceYard caches',async()=>{const lab=fixture();for(const name of ['priceyard-v1-shell','priceyard-v1-data','priceyard-v2-shell','priceyard-v3-shell','unrelated','priceyard-unrelated'])await lab.caches.open(name);await lab.event('activate');assert.ok(!lab.stores.has('priceyard-v1-shell'));assert.ok(!lab.stores.has('priceyard-v1-data'));for(const name of ['priceyard-v2-shell','priceyard-v3-shell','unrelated','priceyard-unrelated'])assert.ok(lab.stores.has(name));});
test('failed fresh HTTP responses never fall back to previous success',async()=>{for(const status of [401,403,404,429,500]){const lab=fixture();await lab.fetch('/api/price-updates');lab.setReply(()=>new Response('{}',{status}));assert.equal((await lab.fetch('/api/price-updates')).response.status,status);}});
test('private and no-store public responses cannot be cached',async()=>{for(const directive of ['private','no-store']){const lab=fixture();lab.setReply(()=>new Response('{}',{headers:{'Content-Type':'application/json','Cache-Control':directive}}));await lab.fetch('/api/price-updates');lab.setOffline();await assert.rejects(()=>lab.fetch('/api/price-updates'));}});
test('cache quota failure does not break successful live response',async()=>{const lab=fixture();lab.failWrites();assert.equal((await lab.fetch('/api/price-updates')).response.status,200);});
test('navigation excludes reset account Admin payment and historical screens',async()=>{for(const endpoint of ['/reset-password?token=SYNTHETIC','/dashboard','/admin','/payment/callback','/history'])assert.equal((await fixture().fetch(endpoint,{mode:'navigate'})).intercepted,false);});
test('same-origin assets remain available without a network',async()=>{const lab=fixture();lab.setReply(()=>new Response('synthetic asset',{headers:{'Content-Type':'text/javascript'}}));await lab.fetch('/assets/synthetic.js');lab.setOffline();assert.equal(await(await lab.fetch('/assets/synthetic.js')).response.text(),'synthetic asset');});
test('public HTML shell fallback never stores an HTTP error',async()=>{const lab=fixture();lab.setReply(()=>new Response('Synthetic public shell',{headers:{'Content-Type':'text/html'}}));await lab.fetch('/prices',{mode:'navigate'});lab.setReply(()=>new Response('Synthetic error',{status:500,headers:{'Content-Type':'text/html'}}));assert.equal((await lab.fetch('/prices',{mode:'navigate'})).response.status,500);lab.setOffline();assert.equal(await(await lab.fetch('/prices',{mode:'navigate'})).response.text(),'Synthetic public shell');});
test('invalid API configuration disables API caching',async()=>{for(const api of ['http://outside.invalid/api','https://user:synthetic@api.invalid/api','https://api.invalid/api?secret=synthetic'])assert.equal((await fixture(api).fetch('/api/price-updates')).intercepted,false);});
test('private fresh response invalidates a formerly public cached copy',async()=>{const lab=fixture();await lab.fetch('/api/price-updates');lab.setReply(()=>new Response('{}',{headers:{'Content-Type':'application/json','Cache-Control':'no-store'}}));await lab.fetch('/api/price-updates');lab.setOffline();await assert.rejects(()=>lab.fetch('/api/price-updates'));});
const failures=[];
for(const [name,run] of tests)try{await run();}catch(error){failures.push({name,error:error.message.slice(0,400)});}
const report={before,tests:tests.length,failures,actual_service_worker_source:true,in_memory_cache_and_fake_fetch:true,native_network_available_to_worker:false,production_connections:0};
fs.writeFileSync(path.join(lab,'runtime/offline-worker'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
if(!before)assert.equal(failures.length,0);
