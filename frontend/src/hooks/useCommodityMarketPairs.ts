import { useEffect, useState } from "react";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";

/** Maps each commodity name to the set of market names that currently have an approved price for it. */
export function useCommodityMarketPairs() {
  const [pairs, setPairs] = useState<Map<string, Set<string>>>(new Map());

  useEffect(() => {
    apiFetch<PriceUpdate[]>("/price-updates")
      .then((items) => {
        const map = new Map<string, Set<string>>();
        for (const item of items) {
          const set = map.get(item.commodity.name) ?? new Set<string>();
          set.add(item.market.name);
          map.set(item.commodity.name, set);
        }
        setPairs(map);
      })
      .catch(() => undefined);
  }, []);

  return pairs;
}
