import { agingClass, relativeTime } from "../utils";

export const PRICE_TIME_LABEL = "Nigeria time (WAT)";
const WAT_OFFSET_MS = 60 * 60 * 1000;

/** Only explicit instants: never guess the zone of an ambiguous legacy value. */
export function priceEpoch(value: string | null | undefined): number {
  return value && /T.*(?:Z|[+-]\d{2}:\d{2})$/i.test(value) ? Date.parse(value) : NaN;
}

export function shortPriceDate(value: string | null | undefined): string {
  if (!value) return "—";
  const epoch = priceEpoch(value);
  if (!Number.isFinite(epoch)) return value;
  return new Intl.DateTimeFormat("en-NG", {
    timeZone: "Africa/Lagos", dateStyle: "medium", timeStyle: "short", hour12: true,
  }).format(epoch) + " WAT";
}

export function relativePriceTime(value: string | null | undefined): string {
  return Number.isFinite(priceEpoch(value)) ? relativeTime(value, shortPriceDate) : value || "—";
}

export function priceAgingClass(value: string | null | undefined): string {
  return Number.isFinite(priceEpoch(value)) ? agingClass(value) : "";
}

/** datetime-local controls represent WAT wall-clock time, regardless of device. */
export function priceInputToUtc(value: string): string {
  return new Date(value + "+01:00").toISOString();
}

export function priceInputNow(): string {
  return new Date(Date.now() + WAT_OFFSET_MS).toISOString().slice(0, 16);
}

export function priceCalendarDate(value: string): string {
  const epoch = priceEpoch(value);
  return Number.isFinite(epoch) ? new Date(epoch + WAT_OFFSET_MS).toISOString().slice(0, 10) : value;
}
