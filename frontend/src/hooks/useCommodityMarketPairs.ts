import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";

type CommodityMarketPair = { commodity: { name: string }; market: { name: string } };

function buildPairs(items: CommodityMarketPair[]): Map<string, Set<string>> {
  const map = new Map<string, Set<string>>();
  for (const item of items) {
    const set = map.get(item.commodity.name) ?? new Set<string>();
    set.add(item.market.name);
    map.set(item.commodity.name, set);
  }
  return map;
}

/** Maps each commodity name to the set of market names that currently have an approved price for it. */
export function useCommodityMarketPairs() {
  const [pairs, setPairs] = useState<Map<string, Set<string>>>(new Map());

  useEffect(() => {
    let current = true;
    apiFetch<PriceUpdate[]>("/price-updates")
      .then((items) => { if (current) setPairs(buildPairs(items)); })
      .catch(() => undefined);
    return () => { current = false; };
  }, []);

  return pairs;
}

/** Same idea, but built from full price history instead of current prices only -- so a market that no longer has a current price, but does have past records, still shows up as a valid filter option. Requires full-access auth. */
export function useHistoricalCommodityMarketPairs(token: string | null | undefined) {
  const [pairs, setPairs] = useState<Map<string, Set<string>>>(new Map());

  useEffect(() => {
    let current = true;
    setPairs(new Map());
    if (!token) return;
    apiFetch<CommodityMarketPair[]>("/price-updates/history/pairs", {}, token)
      .then((items) => { if (current) setPairs(buildPairs(items)); })
      .catch(() => undefined);
    return () => { current = false; };
  }, [token]);

  return pairs;
}
