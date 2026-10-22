import { identityValue, nameSelection, selectionFromQuery } from "./priceIdentity";

const STORAGE_KEY = "priceyard_history_filters_v1";
type CatalogRecord = { id: number; name: string };
type HistoryFilters = { commodity: string; market: string; remembered: boolean };
const validId = (value: unknown): value is number => Number.isSafeInteger(value) && Number(value) > 0;

/** Remember identifiers only, never prices, access credentials or account data. */
export function initialHistoryFilters(query: URLSearchParams): HistoryFilters {
  const defaults = { commodity: nameSelection("Egusi"), market: "", remembered: false };
  if (["commodity_id", "commodity", "market_id", "market"].some(key => query.has(key))) {
    return {
      commodity: query.has("commodity_id") || query.has("commodity")
        ? selectionFromQuery(query, "commodity") : defaults.commodity,
      market: selectionFromQuery(query, "market"), remembered: false,
    };
  }
  try {
    const value: unknown = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (value && typeof value === "object" && !Array.isArray(value)) {
      const saved = value as Record<string, unknown>;
      if ((saved.commodity_id === null || validId(saved.commodity_id)) &&
          (saved.market_id === null || validId(saved.market_id))) {
        return { commodity: saved.commodity_id === null ? "" : identityValue(saved.commodity_id),
          market: saved.market_id === null ? "" : identityValue(saved.market_id), remembered: true };
      }
    }
  } catch { /* Blocked/full/corrupt browser storage must not prevent a search. */ }
  return defaults;
}

export function restoreHistoryFilters(commodity: string, market: string,
  commodities: CatalogRecord[], markets: CatalogRecord[]) {
  const exists = (selection: string, records: CatalogRecord[]) =>
    records.some(record => identityValue(record.id) === selection);
  if (commodity && !exists(commodity, commodities)) {
    const fallback = commodities.find(record => record.name === "Egusi");
    return { commodity: fallback ? identityValue(fallback.id) : "", market: "" };
  }
  return { commodity, market: market && !exists(market, markets) ? "" : market };
}

export function rememberHistoryFilters(commodity: string, market: string,
  commodities: CatalogRecord[], markets: CatalogRecord[]): void {
  const id = (selection: string, records: CatalogRecord[]) =>
    records.find(record => identityValue(record.id) === selection)?.id ?? null;
  const commodityId = id(commodity, commodities), marketId = id(market, markets);
  // An unrecognized link must not overwrite a valid previous search.
  if ((commodity && commodityId === null) || (market && marketId === null)) return;
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ commodity_id: commodityId, market_id: marketId }));
  } catch { /* The current search still works when preferences cannot be saved. */ }
}
