import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(lab,'../..');
const ts=(await import(pathToFileURL(path.join(root,'frontend/node_modules/typescript/lib/typescript.js')))).default;
const source=fs.readFileSync(path.join(root,'frontend/src/services/api.ts'),'utf8').replace('import.meta.env.VITE_API_URL','""');
const compilerOptions={target:ts.ScriptTarget.ES2022,module:ts.ModuleKind.ES2022};
const session=ts.transpileModule(fs.readFileSync(path.join(root,'frontend/src/services/sessionTransport.ts'),'utf8'),{compilerOptions}).outputText;
const sessionUrl='data:text/javascript;base64,'+Buffer.from(session).toString('base64');
const compiled=ts.transpileModule(source,{compilerOptions}).outputText.replace('from "./sessionTransport"','from "'+sessionUrl+'"');
const api=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
let cases=0;const nativeFetch=globalThis.fetch,stamp='2026-10-17T12:00:00.000Z';
try {
  globalThis.fetch=async()=>new Response('[{"id":1}]',{headers:{'Content-Type':'application/json'}});
  assert.deepEqual(await api.apiFetchWithProvenance('/price-updates'),{data:[{id:1}],savedAt:null});cases++;
  globalThis.fetch=async()=>new Response('[{"id":1}]',{headers:{'X-PriceYard-Cache':'saved','X-PriceYard-Saved-At':stamp}});
  assert.deepEqual(await api.apiFetchWithProvenance('/price-updates'),{data:[{id:1}],savedAt:stamp});cases++;
  for(const value of [null,'invalid','2026-10-17']){
    globalThis.fetch=async()=>new Response('[]',{headers:{'X-PriceYard-Cache':'saved',...(value?{'X-PriceYard-Saved-At':value}:{})}});
    await assert.rejects(()=>api.apiFetchWithProvenance('/price-updates'),error=>error instanceof api.ApiError&&error.status===503);cases++;
  }
  globalThis.fetch=async()=>new Response('[]',{headers:{'X-PriceYard-Saved-At':stamp}});
  assert.deepEqual(await api.apiFetchWithProvenance('/price-updates'),{data:[],savedAt:null});cases++;
  const controller=new AbortController();
  globalThis.fetch=async(_url,options)=>{
    assert.equal(options.signal,controller.signal);assert.equal(options.credentials,'omit');
    return new Response('[]',{headers:{'X-PriceYard-Cache':'saved','X-PriceYard-Saved-At':stamp}});
  };
  assert.deepEqual(await api.apiFetchWithProvenance('/price-updates',{signal:controller.signal}),{data:[],savedAt:stamp});cases++;
  globalThis.fetch=(_url,options)=>new Promise((_resolve,reject)=>{
    options.signal.addEventListener('abort',()=>reject(new DOMException('Synthetic cancellation','AbortError')),{once:true});
  });
  const pending=api.apiFetchWithProvenance('/price-updates',{signal:controller.signal});controller.abort();
  await assert.rejects(pending,error=>error.name==='AbortError');cases++;
  for(const status of [401,403,429,500]) {
    let token;api.setUnauthorizedHandler(value=>token=value);
    globalThis.fetch=async()=>new Response('{"detail":"Synthetic failure"}',{status});
    await assert.rejects(()=>api.apiFetch('/synthetic',{},'SYNTHETIC-TOKEN'),error=>error.status===status&&error.detail==='Synthetic failure');
    assert.equal(token,status===401?'SYNTHETIC-TOKEN':undefined);cases++;
  }
  globalThis.fetch=async()=>new Response(null,{status:204});
  assert.equal(await api.apiFetch('/synthetic',{method:'DELETE'}),undefined);cases++;
  let notified=false;globalThis.fetch=async()=>new Response('invalid JSON');
  await assert.rejects(()=>api.apiFetch('/price-updates',{},null,()=>notified=true));assert.equal(notified,false);cases++;
  const report={cases,passed:cases,actual_api_typescript:true,invalid_cache_timestamps_fail_closed:true,original_401_handler_preserved:true,only_fake_fetch_used:true,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/offline-api-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
} finally {globalThis.fetch=nativeFetch;api.setUnauthorizedHandler(null);}
