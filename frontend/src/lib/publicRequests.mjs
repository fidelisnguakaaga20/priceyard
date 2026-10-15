// Share only simultaneous anonymous reads; never retain responses as a cache.
const pending = new Map();
export function coalescePublicRead(key, load) {
  if (pending.has(key)) return pending.get(key).then((value) => JSON.parse(JSON.stringify(value)));
  const operation = Promise.resolve().then(load);
  pending.set(key, operation);
  operation.then(() => pending.delete(key), () => pending.delete(key));
  return operation.then((value) => JSON.parse(JSON.stringify(value)));
}
