import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath,pathToFileURL} from 'node:url';
const lab=path.dirname(fileURLToPath(import.meta.url));
const root=path.resolve(lab,'../..');
const ts=await import(pathToFileURL(path.join(root,'frontend/node_modules/typescript/lib/typescript.js')));
const helper=path.join(root,'frontend/src/services/access.ts');
let source;
if(fs.existsSync(helper))source=fs.readFileSync(helper,'utf8');
else {
  const auth=fs.readFileSync(path.join(root,'frontend/src/context/AuthContext.tsx'),'utf8');
  source='export '+auth.slice(auth.indexOf('function computeAccess('),auth.indexOf('export function AuthProvider('));
}
const compiled=ts.default.transpileModule(source,{compilerOptions:{target:ts.default.ScriptTarget.ES2022,module:ts.default.ModuleKind.ES2022}}).outputText;
const {computeAccess}=await import('data:text/javascript;base64,'+Buffer.from(compiled).toString('base64'));
process.env.TZ='Africa/Lagos';
const originalNow=Date.now;
Date.now=()=>Date.parse('2026-10-16T11:30:00Z');
const free={role:'free_user'};
const paid={role:'paid_user'};
const trial={status:'trial',trial_ends_at:'2026-10-16T12:00:00Z',end_date:null};
const cases=[
  ['guest',null,null,{label:'Guest',full:false}],
  ['administrator',{role:'admin'},null,{label:'Admin',full:true}],
  ['free',free,{status:'free'},{label:'Free',full:false}],
  ['active trial',free,trial,{label:'Trial',full:true}],
  ['expired trial',free,{...trial,trial_ends_at:'2026-10-16T11:29:59Z'},{label:'Free',full:false}],
  ['exact trial deadline',free,{...trial,trial_ends_at:'2026-10-16T11:30:00Z'},{label:'Free',full:false}],
  ['missing trial deadline',free,{...trial,trial_ends_at:null},{label:'Free',full:false}],
  ['invalid trial deadline',free,{...trial,trial_ends_at:'invalid'},{label:'Free',full:false}],
  ['legacy naive trial means UTC',free,{...trial,trial_ends_at:'2026-10-16T12:00:00'},{label:'Trial',full:true}],
  ['paid through end date',paid,{status:'active',end_date:'2026-10-16'},{label:'Active Paid',full:true}],
  ['future paid date',paid,{status:'active',end_date:'2026-11-15'},{label:'Active Paid',full:true}],
  ['expired paid date',paid,{status:'active',end_date:'2026-10-15'},{label:'Free',full:false}],
  ['cancelled with old paid role',paid,{status:'cancelled',end_date:'2026-11-15'},{label:'Free',full:false}],
  ['expired with old paid role',paid,{status:'expired',end_date:'2026-10-15'},{label:'Free',full:false}],
  ['missing subscription with paid role',paid,null,{label:'Free',full:false}],
  ['indefinite manual grant',paid,{status:'active',end_date:null},{label:'Active Paid',full:true}],
  ['invalid date fails closed',paid,{status:'active',end_date:'2026-02-31'},{label:'Free',full:false}],
  ['reporter authority alone is not paid',{role:'reporter'},{status:'free'},{label:'Free',full:false}],
];
const failures=[];
try {
  for(const [name,user,subscription,expected] of cases) {
    try{assert.deepEqual(computeAccess(user,subscription),expected)}catch{failures.push(name)}
  }
  const before=process.argv.includes('--expect-bug');
  const report={cases:cases.length,passed:cases.length-failures.length,failures,production_connections:0};
  fs.writeFileSync(path.join(lab,'runtime/access-unit'+(before?'-before':'')+'.json'),JSON.stringify(report,null,2));
  console.log(JSON.stringify(report));
  if(before)assert.ok(failures.length>0);else assert.deepEqual(failures,[]);
}finally{Date.now=originalNow;}
