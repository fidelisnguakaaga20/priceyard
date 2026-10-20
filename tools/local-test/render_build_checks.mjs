// Validate the real Vite configuration in the marked, credential-free snapshot.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath, pathToFileURL} from 'node:url';
const lab = path.dirname(fileURLToPath(import.meta.url));
const target = path.resolve(process.argv[2] || '');
assert.equal(path.dirname(target), path.join(lab, 'runtime'));
assert.ok(path.basename(target).startsWith('frontend-'));
const {loadConfigFromFile} = await import(pathToFileURL(path.join(target, 'node_modules/vite/dist/node/index.js')));
const original = process.env.VITE_API_URL;
let checked = 0;
try {
  for (const value of ['/api', '/api/', '']) {
    process.env.VITE_API_URL = value;
    const loaded = await loadConfigFromFile({command:'build', mode:'production'}, path.join(target, 'vite.config.ts'), target, 'silent');
    assert.ok(loaded?.config); checked++;
  }
  for (const value of ['https://priceyard-api.onrender.com', '//priceyard-api.onrender.com/api', 'http://example.invalid', '/api?target=external']) {
    process.env.VITE_API_URL = value;
    await assert.rejects(() => loadConfigFromFile({command:'build', mode:'production'}, path.join(target, 'vite.config.ts'), target, 'silent'), /require VITE_API_URL=\/api/);
    checked++;
  }
  const result = {status:'passed', cases:checked, scope:'actual production Vite configuration admission; no network or credentials', rejected_cross_site_API_builds:true};
  fs.writeFileSync(path.join(lab, 'runtime/render-build-checks.json'), JSON.stringify(result, null, 2));
  process.stdout.write(JSON.stringify(result)+'\n');
} finally {
  if (original === undefined) delete process.env.VITE_API_URL; else process.env.VITE_API_URL = original;
}
