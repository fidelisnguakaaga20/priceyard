import { useEffect, useState } from "react";
import { usePreferences } from "../context/PreferencesContext";
import { apiFetch } from "../services/api";
import type { PriceUpdate } from "../types/api";

function buildPairs(items: PriceUpdate[]): Map<string, Set<string>> {
  const pairs = new Map<string, Set<string>>();
  for (const item of items) {
    const markets = pairs.get(item.commodity.name) ?? new Set<string>();
    markets.add(item.market.name);
    pairs.set(item.commodity.name, markets);
  }
  return pairs;
}

/** Convenience ordering only; price queries and target alerts use stable IDs. */
export function useCommodityMarketPairs() {
  const { dataSaver } = usePreferences();
  const [pairs, setPairs] = useState<Map<string, Set<string>>>(new Map());
  useEffect(() => {
    let active = true;
    const controller = new AbortController();
    const refresh = () => {
      void apiFetch<PriceUpdate[]>("/price-updates", { signal: controller.signal })
        .then((items) => { if (active) setPairs(buildPairs(items)); }).catch(() => undefined);
    };
    refresh();
    const timer = dataSaver ? undefined : setInterval(refresh, 60_000);
    window.addEventListener("priceyard:approved-price", refresh);
    return () => { active = false; controller.abort(); clearInterval(timer); window.removeEventListener("priceyard:approved-price", refresh); };
  }, [dataSaver]);
  return pairs;
}
