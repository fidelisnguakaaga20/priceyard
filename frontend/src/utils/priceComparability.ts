import type { PriceUpdate } from "../types/api";

import { priceEpoch } from "./priceTime";

const unknownValues = new Set(["", "unknown", "not known", "not specified", "not confirmed", "not available", "not provided", "n/a", "na", "none", "unspecified", "—", "-", "?"]);
const normalized = (value: string | null | undefined) => (value ?? "").trim().toLowerCase();

/** Only existing recorded specifications; no quantity conversion or inferred type. */
export function comparablePriceGroups(items: PriceUpdate[]): PriceUpdate[][] {
  const groups = new Map<string, PriceUpdate[]>();
  for (const item of items) {
    const specifications = [normalized(item.unit), normalized(item.bag_size), normalized(item.commodity_type)];
    if (specifications.some((value) => unknownValues.has(value))) continue;
    const values = [Number(item.price_low), Number(item.price_high), priceEpoch(item.update_date_time)];
    if (!values.every(Number.isFinite) || values[0] < 0 || values[1] < values[0]) continue;
    if (item.average_price != null) {
      const average = Number(item.average_price);
      if (!Number.isFinite(average) || average < values[0] || average > values[1]) continue;
    }
    const key = JSON.stringify([item.commodity_id, item.market_id, ...specifications]);
    const group = groups.get(key) ?? [];
    group.push(item); groups.set(key, group);
  }
  return [...groups.values()].map((group) => [...group].sort((a, b) =>
    priceEpoch(a.update_date_time) - priceEpoch(b.update_date_time) || a.id - b.id));
}
