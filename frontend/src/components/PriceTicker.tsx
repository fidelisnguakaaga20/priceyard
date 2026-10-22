import { useState } from "react";
import type { PriceUpdate } from "../types/api";
import { money, movementIcon } from "../utils";
import { SavedPriceNotice } from "./SavedPriceNotice";
import "./PriceTicker.css";

/** The repeated price track is decorative; its scrolling control remains
 * available to keyboard and screen-reader users. Pausing never stops updates. */
export function PriceTicker({ items, savedAt = null }: { items: PriceUpdate[]; savedAt?: string | null }) {
  const [scrollingPaused, setScrollingPaused] = useState(false);
  if (!items.length) return null;
  const track = [...items, ...items];

  return (
    <><SavedPriceNotice savedAt={savedAt} /><div className="price-ticker price-ticker-controls" data-scrolling-paused={scrollingPaused}>
      <div className="price-ticker-viewport" aria-hidden="true"><div className="price-ticker-track">
        {track.map((item, index) => (
          <span className="price-ticker-item" key={`${item.id}-${index}`}>
            {item.commodity.name}{" "}
            <strong>{money(item.price_low)}–{money(item.price_high)}</strong>{" "}
            <span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)}</span>
            <span className="price-ticker-market">{[item.unit, item.bag_size, item.commodity_type].filter(Boolean).join(" · ")} @ {item.market.name}</span>
          </span>
        ))}
      </div></div>
      <button
        type="button"
        className="price-ticker-toggle"
        aria-label={scrollingPaused ? "Resume scrolling" : "Pause scrolling"}
        aria-pressed={scrollingPaused}
        title="Only pauses scrolling; prices still refresh."
        onClick={() => setScrollingPaused((paused) => !paused)}
      >
        <span aria-hidden="true">{scrollingPaused ? "▶" : "Ⅱ"}</span>
        {scrollingPaused ? "Resume" : "Pause"}
      </button>
    </div></>
  );
}
