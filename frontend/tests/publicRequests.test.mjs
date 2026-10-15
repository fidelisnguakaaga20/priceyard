import assert from 'node:assert/strict';
import test from 'node:test';
import { coalescePublicRead } from '../src/lib/publicRequests.mjs';

test('simultaneous public prices use one read with independent consumer objects', async () => {
  let calls = 0;
  const load = async () => { calls++; return [{ id: 1, bag_size: '50kg' }]; };
  const [ticker, home] = await Promise.all([coalescePublicRead('/price-updates', load), coalescePublicRead('/price-updates', load)]);
  assert.equal(calls, 1);
  ticker[0].bag_size = '25kg';
  assert.equal(home[0].bag_size, '50kg');
  await coalescePublicRead('/price-updates', load);
  assert.equal(calls, 2, 'a later refresh must reach the API');
});

test('a failed public read can be retried and filters keep independent results', async () => {
  await assert.rejects(coalescePublicRead('/price-updates', async () => { throw new Error('Synthetic outage'); }));
  assert.deepEqual(await coalescePublicRead('/price-updates', async () => [1]), [1]);
  const results = await Promise.all([
    coalescePublicRead('/price-updates?market_id=1', async () => [1]),
    coalescePublicRead('/price-updates?market_id=2', async () => [2]),
  ]);
  assert.deepEqual(results, [[1], [2]]);
});
