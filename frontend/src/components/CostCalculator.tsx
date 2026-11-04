import { useState } from "react";
import type { CostBreakdown } from "../types/api";
import { money } from "../utils";

export function CostCalculator({ breakdown }: { breakdown: CostBreakdown }) {
  const [quantity, setQuantity] = useState("1");
  const safeQuantity = Math.max(0, Number(quantity) || 0);

  const purchaseTotal = Number(breakdown.purchase_price_reference) * safeQuantity;
  const grandTotal = Number(breakdown.total_estimated_landing_storage_cost) * safeQuantity;

  return (
    <div className="cost-calculator">
      <h4>💰 Use calculator</h4>
      <p className="muted">Enter how many units you're buying to see your total cost.</p>
      <div className="form-stack">
        <label>How many are you buying?
          <input type="number" min="0" step="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
        </label>
      </div>
      <dl className="data-list compact">
        <div><dt>Purchase cost</dt><dd>{money(purchaseTotal)}</dd></div>
      </dl>
      {breakdown.cost_items?.length ? <p className="cost-items-line">{breakdown.cost_items.map((item) => `${item.name} ${money(Number(item.amount) * safeQuantity)}`).join(" · ")}</p> : null}
      <div className="cost-total"><span>Estimated Total cost</span><strong>{money(grandTotal)}</strong></div>
    </div>
  );
}
