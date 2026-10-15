import assert from "node:assert/strict";
import test from "node:test";
import { adminPagePath, createLatestRequestGate, supportsAdminPaging } from "../src/lib/adminPaging.mjs";

test("known administrative lists retain filters and request the selected bounded page", () => {
  const path = adminPagePath("/feedback?rating=4", 2);
  const parameters = new URLSearchParams(path.split("?")[1]);
  assert.equal(parameters.get("rating"), "4");
  assert.equal(parameters.get("page"), "2");
  assert.equal(parameters.get("page_size"), "100");
  assert.equal(supportsAdminPaging("/price-updates/admin/flagged"), true);
  assert.equal(supportsAdminPaging("/cost-breakdowns"), true);
});

test("catalogs, detail and aggregate endpoints never receive unsupported paging", () => {
  for (const path of ["/commodities/admin/all", "/markets/admin/all", "/faq/admin/all", "/feedback/summary", "/users/1"]) {
    assert.equal(supportsAdminPaging(path), false);
    assert.equal(adminPagePath(path, 2), path);
  }
  assert.equal(adminPagePath("/users?custom=value", 2, 100, false), "/users?custom=value");
});

test("page navigation replaces query values and rejects invalid bounds", () => {
  const path = adminPagePath("/users?page=99&page_size=1000", 3, 100);
  assert.equal(path, "/users?page=3&page_size=100");
  for (const args of [[0, 100], [1.5, 100], [1, 1001]]) {
    assert.throws(() => adminPagePath("/users", ...args), RangeError);
  }
});

test("a delayed earlier response cannot replace a newer page", async () => {
  const gate = createLatestRequestGate();
  let finishEarlier;
  let displayed;
  const earlier = gate.begin();
  const delayed = new Promise((resolve) => { finishEarlier = resolve; });
  const staleOperation = delayed.then((value) => { if (earlier.isCurrent()) displayed = value; });
  const newer = gate.begin();
  if (newer.isCurrent()) displayed = "newer page";
  finishEarlier("earlier page");
  await staleOperation;
  assert.equal(earlier.signal.aborted, true);
  assert.equal(displayed, "newer page");
  assert.equal(newer.isCurrent(), true);
});

test("unmount cancellation prevents late data and errors from being published", () => {
  const gate = createLatestRequestGate();
  const operation = gate.begin();
  gate.cancel();
  assert.equal(operation.signal.aborted, true);
  assert.equal(operation.isCurrent(), false);
});
