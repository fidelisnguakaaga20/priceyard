import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url)),root=path.resolve(lab,'../..');
const ts=await import(pathToFileURL(path.join(root,'frontend/node_modules/typescript/lib/typescript.js')));
const source=fs.readFileSync(path.join(root,'frontend/src/utils/priceComparability.ts'),'utf8');
const compiled=ts.default.transpileModule(source,{compilerOptions:{target:ts.default.ScriptTarget.ES2022,module:ts.default.ModuleKind.ES2022}}).outputText;
const {comparablePriceGroups}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
const base={id:1,commodity_id:1,market_id:1,unit:'1 bag',bag_size:'synthetic recorded size',commodity_type:'synthetic recorded type',price_low:210000,price_high:220000,average_price:215000,update_date_time:'2026-10-17T08:00:00Z'};
let cases=0;
for(const field of ['commodity_id','market_id','unit','bag_size','commodity_type']){
 const second={...base,id:2,[field]:field.endsWith('_id')?2:'different recorded text'};
 assert.deepEqual(comparablePriceGroups([base,second]).map(group=>group.length),[1,1]);cases++;
}
for(const value of [null,'','Unknown','N/A','not specified','?'])for(const field of ['unit','bag_size','commodity_type']){
 assert.deepEqual(comparablePriceGroups([{...base,[field]:value}]),[]);cases++;
}
for(const changes of [{price_low:-1},{price_low:230000},{price_high:NaN},{average_price:Infinity},{average_price:300000},{update_date_time:'invalid'}]){
 assert.deepEqual(comparablePriceGroups([{...base,...changes}]),[]);cases++;
}
const first=Object.freeze({...base,id:2}),second=Object.freeze({...base,id:1,unit:' 1 BAG ',bag_size:' SYNTHETIC RECORDED SIZE ',commodity_type:' SYNTHETIC RECORDED TYPE '});
const input=Object.freeze([first,second]);assert.deepEqual(comparablePriceGroups(input).map(group=>group.map(row=>row.id)),[[1,2]]);assert.equal(input[0].id,2);cases++;
assert.deepEqual(comparablePriceGroups([{...base,average_price:null}]).map(group=>group.length),[1]);cases++;
const report={cases,passed:cases,no_inferred_weights_or_types:true,original_inputs_unchanged:true,production_connections:0};
fs.writeFileSync(path.join(lab,'runtime/comparison-unit-checks.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report));
