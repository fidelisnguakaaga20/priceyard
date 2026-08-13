const fs = require("fs");
const path = require("path");
const ts = require("/opt/nvm/versions/node/v22.16.0/lib/node_modules/typescript");
const root = path.resolve(__dirname, "../../frontend/src");
let failed = false;
let count = 0;
function walk(dir) {
  for (const name of fs.readdirSync(dir)) {
    const file = path.join(dir, name);
    const stat = fs.statSync(file);
    if (stat.isDirectory()) walk(file);
    else if (/\.(ts|tsx)$/.test(name) && !name.endsWith(".d.ts")) {
      count += 1;
      const result = ts.transpileModule(fs.readFileSync(file, "utf8"), {
        compilerOptions: { jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.ESNext },
        reportDiagnostics: true,
        fileName: file,
      });
      if ((result.diagnostics || []).length) {
        failed = true;
        console.log("FAIL", file);
        for (const diagnostic of result.diagnostics) console.log(ts.flattenDiagnosticMessageText(diagnostic.messageText, "\n"));
      }
    }
  }
}
walk(root);
console.log(`Stage 18 TS/TSX files checked: ${count}`);
console.log(`STAGE 18 TYPESCRIPT SYNTAX: ${failed ? "FAIL" : "PASS"}`);
process.exit(failed ? 1 : 0);
