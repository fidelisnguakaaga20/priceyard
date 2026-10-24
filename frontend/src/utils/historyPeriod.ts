import { priceEpoch } from "./priceTime";

export type HistoryPeriod = "all" | "7" | "30";
const DAY_MS = 86_400_000;
const WAT_OFFSET_MS = 3_600_000;

/** Calendar days in Nigeria, including today; no guessed dates or device zone. */
export function historyPeriodBounds(period: HistoryPeriod, now = Date.now()) {
  if (period === "all") return null;
  const today = Math.floor((now + WAT_OFFSET_MS) / DAY_MS) * DAY_MS - WAT_OFFSET_MS;
  return { start: today - (Number(period) - 1) * DAY_MS, end: today + DAY_MS };
}

export function historyInPeriod<T extends { update_date_time: string }>(items: T[], period: HistoryPeriod, now = Date.now()): T[] {
  const bounds = historyPeriodBounds(period, now);
  if (!bounds) return items;
  return items.filter(item => {
    const time = priceEpoch(item.update_date_time);
    return Number.isFinite(time) && time >= bounds.start && time < bounds.end;
  });
}

export function historyPeriodDescription(period: HistoryPeriod, now = Date.now()): string {
  const bounds = historyPeriodBounds(period, now);
  if (!bounds) return "All recorded dates";
  const format = new Intl.DateTimeFormat("en-NG", {
    timeZone: "Africa/Lagos", day: "numeric", month: "short", year: "numeric",
  });
  return `${format.format(bounds.start)} – ${format.format(bounds.end - 1)} (WAT, including today)`;
}
