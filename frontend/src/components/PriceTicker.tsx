import type { PriceUpdate } from "../types/api";
import { money, movementIcon } from "../utils";

/** A continuously-scrolling strip of live current prices, shown at the top of the
 * homepage. Purely decorative/redundant with the real price cards further down the
 * page, so it's hidden from screen readers and pauses on hover/focus for anyone who
 * wants to actually read it. */
export function PriceTicker({ items }: { items: PriceUpdate[] }) {
  if (!items.length) return null;
  const track = [...items, ...items];

  return (
    <div className="price-ticker" aria-hidden="true">
      <div className="price-ticker-track">
        {track.map((item, index) => (
          <span className="price-ticker-item" key={`${item.id}-${index}`}>
            {item.commodity.name}{" "}
            <strong>{money(item.price_low)}–{money(item.price_high)}</strong>{" "}
            <span className={`movement movement-${item.movement}`}>{movementIcon(item.movement)}</span>
            <span className="price-ticker-market">@ {item.market.name}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
