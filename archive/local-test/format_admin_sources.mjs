// Local-only readability pass. Refuse any change to emitted application code.
import assert from 'node:assert/strict';
import fs from 'node:fs';
import { createHash } from 'node:crypto';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const lab = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(lab, '../..');
const marker = JSON.parse(fs.readFileSync(path.join(lab, 'runtime/frontend.json'), 'utf8').replace(/^\uFEFF/, ''));
assert.equal(marker.purpose, 'synthetic-only-no-application-credentials');
const snapshot = path.resolve(marker.path);
assert.equal(path.dirname(snapshot), path.join(lab, 'runtime'));
const require = createRequire(path.join(snapshot, 'package.json'));
const ts = require('typescript');
const printer = ts.createPrinter({ newLine: ts.NewLineKind.LineFeed });
const files = ['AdminIntelligencePages.tsx', 'AdminSignalsPage.tsx'];
const report = [];

function parse(text, name) {
  const ast = ts.createSourceFile(name, text, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
  assert.equal(ast.parseDiagnostics.length, 0, 'Source must parse before formatting');
  return ast;
}
function executable(text, name) {
  const result = ts.transpileModule(text, { fileName: name, compilerOptions: {
    target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ESNext,
    jsx: ts.JsxEmit.ReactJSX, removeComments: true, sourceMap: false,
  }});
  const emitted = ts.createSourceFile('checked.js', result.outputText, ts.ScriptTarget.Latest, true);
  assert.equal(emitted.parseDiagnostics.length, 0);
  function syntax(node) {
    const children = [];
    ts.forEachChild(node, child => { children.push(syntax(child)); });
    return [node.kind, ts.isSourceFile(node) ? null : node.text ?? null, node.operator ?? null,
      ts.isVariableDeclarationList(node) ? node.flags & ts.NodeFlags.BlockScoped : null, children];
  }
  return createHash('sha256').update(JSON.stringify(syntax(emitted))).digest('hex');
}

for (const name of files) {
  const location = path.join(root, 'frontend/src/pages/admin', name);
  const original = fs.readFileSync(location, 'utf8');
  const ast = parse(original, name);
  const breaks = new Set();
  function lineBefore(at) {
    if (original.slice(original.lastIndexOf('\n', at - 1) + 1, at).trim()) breaks.add(at);
  }
  function visit(node) {
    // Add layout whitespace only inside JSX, never between `return` and its value.
    const nestedOpening = ts.isJsxOpeningElement(node) && ts.isJsxElement(node.parent.parent);
    const child = ts.isJsxSelfClosingElement(node) && ts.isJsxElement(node.parent);
    if (nestedOpening || child || ts.isJsxClosingElement(node)) {
      lineBefore(node.getStart(ast));
    }
    if (ts.isStatement(node) && (ts.isBlock(node.parent) || ts.isSourceFile(node.parent))) lineBefore(node.getStart(ast));
    if (ts.isObjectLiteralExpression(node)) {
      for (const property of node.properties) lineBefore(property.getStart(ast));
      if (node.properties.length) lineBefore(node.end - 1);
    }
    if (ts.isBlock(node) && node.statements.length) lineBefore(node.end - 1);
    ts.forEachChild(node, visit);
  }
  visit(ast);
  let spaced = original;
  for (const at of [...breaks].sort((a, b) => b - a)) spaced = spaced.slice(0, at) + '\n' + spaced.slice(at);
  const formatted = printer.printFile(parse(spaced, name));
  assert.equal(executable(formatted, name), executable(original, name), 'Formatting must preserve emitted code including JSX text');
  const baseline = fs.readFileSync(path.join(snapshot, 'src/pages/admin', name), 'utf8');
  assert.equal(executable(formatted, name), executable(baseline, name), 'Formatting must also preserve the last verified build source');
  report.push({ file: name, emitted_syntax_identical: true,
    verified_build_syntax_identical: true, emitted_syntax_sha256: executable(formatted, name),
    original_lines: original.split('\n').length, formatted_lines: formatted.split('\n').length });
  fs.writeFileSync(location, formatted, 'utf8');
}
fs.writeFileSync(path.join(lab, 'runtime/admin-formatting.json'), JSON.stringify({ files: report, dependencies_installed: 0 }, null, 2));
console.log(JSON.stringify(report));
