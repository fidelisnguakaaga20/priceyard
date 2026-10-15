const normalized = (value) => String(value ?? "").trim().toLocaleLowerCase("en-NG");

export function measurementLabel(item) {
  return [item.unit || "Unit not recorded", item.bag_size || "Package size not recorded",
    item.commodity_type, item.grade && `Grade: ${item.grade}`].filter(Boolean).join(" / ");
}

export function seriesKey(item) {
  // Legacy package sizes cannot be inferred. Keep their observations separate.
  const specification = item.bag_size
    ? [item.unit, item.bag_size, item.commodity_type, item.grade].map(normalized)
    : ["legacy-unspecified", String(item.id)];
  return JSON.stringify([item.commodity_id, item.market_id, ...specification]);
}

export function groupComparablePrices(items) {
  const groups = new Map();
  for (const item of items) {
    const key = seriesKey(item);
    const group = groups.get(key) ?? [];
    group.push(item);
    groups.set(key, group);
  }
  return [...groups.entries()].map(([key, records]) => ({
    key, records: [...records].sort((a, b) =>
      Date.parse(a.update_date_time) - Date.parse(b.update_date_time) || a.id - b.id),
  }));
}

export function reconcileRecords(authoritative, local) {
  const ids = new Set(authoritative.map((item) => item.id));
  return [...authoritative, ...local.filter((item) => !ids.has(item.id))];
}

export function lagosDay(now = new Date()) {
  const parts = new Intl.DateTimeFormat("en-GB", {
    timeZone: "Africa/Lagos", year: "numeric", month: "2-digit", day: "2-digit",
  }).formatToParts(now);
  const get = (type) => parts.find((item) => item.type === type)?.value;
  return `${get("year")}-${get("month")}-${get("day")}`;
}

export function outsideDateWindow(from, to, day = lagosDay()) {
  return Boolean((from && day < from) || (to && day > to));
}

export function toUtcFromLagos(value) {
  if (!/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}(?::\d{2})?$/.test(value)) throw new Error("Enter a valid Nigerian date and time.");
  const date = new Date(`${value}+01:00`);
  if (!Number.isFinite(date.getTime()) || new Date(date.getTime() + 3600000).toISOString().slice(0, value.length) !== value) throw new Error("Enter a valid Nigerian date and time.");
  return date.toISOString();
}

export function matchesTargetBasis(target, price) {
  return target.target_measurement_confirmed === true &&
    target.commodity_id === price.commodity_id && target.market_id === price.market_id &&
    normalized(target.target_unit) === normalized(price.unit) &&
    normalized(target.target_bag_size) === normalized(price.bag_size) &&
    normalized(target.target_commodity_type) === normalized(price.commodity_type) &&
    normalized(target.target_grade) === normalized(price.grade);
}

export function paidCutoffValue(subscription) {
  if (subscription.paid_expires_at) return subscription.paid_expires_at;
  if (!subscription.end_date) return null;
  const midnight = Date.parse(`${subscription.end_date}T00:00:00Z`);
  return Number.isFinite(midnight) ? new Date(midnight + 86400000).toISOString() : null;
}
