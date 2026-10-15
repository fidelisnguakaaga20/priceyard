import { test } from "node:test";
import assert from "node:assert/strict";
import { groupComparablePrices, lagosDay, outsideDateWindow, reconcileRecords, seriesKey, toUtcFromLagos, matchesTargetBasis, paidCutoffValue } from "../src/lib/priceSeries.mjs";

const observation = (id, overrides = {}) => ({
  id, commodity_id: 1, market_id: 1, unit: "1 bag", bag_size: "50kg",
  commodity_type: "white", grade: "A", update_date_time: `2026-10-${String(id).padStart(2, "0")}T10:00:00Z`, ...overrides,
});

test("market, package, quantity, variant and grade remain separate", () => {
  const base = observation(1);
  for (const difference of [{ market_id: 2 }, { commodity_id: 2 }, { unit: "2 bags" },
    { bag_size: "100kg" }, { commodity_type: "brown" }, { grade: "B" }]) {
    assert.notEqual(seriesKey(base), seriesKey(observation(2, difference)));
  }
});
test("legacy missing measurements are not joined", () => {
  assert.notEqual(seriesKey(observation(1, { bag_size: null })), seriesKey(observation(2, { bag_size: null })));
});
test("charts sort comparable observations without changing inputs", () => {
  const items = [observation(2), observation(1)];
  assert.deepEqual(groupComparablePrices(items)[0].records.map((item) => item.id), [1, 2]);
  assert.deepEqual(items.map((item) => item.id), [2, 1]);
});
test("authoritative approval wins over a locally-created pending row", () => {
  assert.deepEqual(reconcileRecords([{ id: 1, status: "approved" }], [{ id: 1, status: "pending" }]), [{ id: 1, status: "approved" }]);
});
test("Lagos day and one-sided windows are explicit", () => {
  assert.equal(lagosDay(new Date("2026-10-13T23:15:00Z")), "2026-10-14");
  assert.equal(outsideDateWindow("2026-10-15", null, "2026-10-14"), true);
  assert.equal(outsideDateWindow(null, "2026-10-13", "2026-10-14"), true);
  assert.equal(outsideDateWindow(null, "2026-10-14", "2026-10-14"), false);
});
test("Nigeria form times do not depend on the device timezone", () => {
  assert.equal(toUtcFromLagos("2026-10-14T00:15"), "2026-10-13T23:15:00.000Z");
  assert.throws(() => toUtcFromLagos("invalid"));
  assert.throws(() => toUtcFromLagos("2026-02-31T10:00"));
});
test("target alerts require confirmed exact market and measurement", () => {
  const target = { commodity_id: 1, market_id: 1, target_unit: "1 bag", target_bag_size: "50kg",
    target_commodity_type: "white", target_grade: "A", target_measurement_confirmed: true };
  assert.equal(matchesTargetBasis(target, observation(1)), true);
  assert.equal(matchesTargetBasis({ ...target, target_measurement_confirmed: false }, observation(1)), false);
  assert.equal(matchesTargetBasis(target, observation(1, { bag_size: "100kg" })), false);
  assert.equal(matchesTargetBasis(target, observation(1, { market_id: 2 })), false);
  assert.equal(matchesTargetBasis({ ...target, target_grade: null }, observation(1)), false);
});
test("legacy paid cutoff includes the entire recorded UTC end date", () => {
  assert.equal(paidCutoffValue({ end_date: "2026-10-14" }), "2026-10-15T00:00:00.000Z");
  assert.equal(paidCutoffValue({ end_date: "2026-10-14", paid_expires_at: "2026-10-15T12:15:00Z" }), "2026-10-15T12:15:00Z");
  assert.equal(paidCutoffValue({ end_date: null }), null);
});
