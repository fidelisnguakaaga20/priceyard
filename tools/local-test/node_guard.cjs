// Applied before frontend tooling. No live transport or dotenv/credential reads.
const fs = require("node:fs");
const path = require("node:path");
function checkFile(value) {
  if (typeof value !== "string" && !(value instanceof URL)) return;
  const name = path.basename(String(value));
  if (name.startsWith(".env") || /\.(pem|key)$/i.test(name)) throw new Error("Secret-bearing file access forbidden in synthetic tooling");
}
for (const method of ["open", "openSync", "readFile", "readFileSync"]) {
  const original = fs[method];
  fs[method] = function(file, ...args) { checkFile(file); return original.call(this, file, ...args); };
}
for (const method of ["open", "readFile"]) {
  const original = fs.promises[method];
  fs.promises[method] = function(file, ...args) { checkFile(file); return original.call(this, file, ...args); };
}
const denied = () => { throw new Error("Live network transport forbidden in synthetic frontend tooling"); };
require("node:net").Socket.prototype.connect = denied;
require("node:tls").connect = denied;
for (const protocol of ["node:http", "node:https"]) {
  require(protocol).request = denied;
  require(protocol).get = denied;
}
for (const method of ["lookup", "resolve", "resolve4", "resolve6"]) {
  require("node:dns")[method] = denied;
  require("node:dns").promises[method] = denied;
}
globalThis.fetch = denied;
if (process.env.PRICEYARD_PWA_TEST === "isolated-loopback") {
  // No DNS query: the PWA fixture binds this one literal local address only.
  require("node:dns").lookup = (host, options, callback) => {
    if (host !== "127.0.0.1") return denied();
    if (typeof options === "function") callback = options;
    process.nextTick(() => callback(null, "127.0.0.1", 4));
  };
  const originalListen = require("node:net").Server.prototype.listen;
  require("node:net").Server.prototype.listen = function(...args) {
    if (args[0] !== 55441 || args[1] !== "127.0.0.1") return denied();
    return originalListen.apply(this, args);
  };
}
