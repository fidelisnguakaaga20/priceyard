import { useState } from "react";
import type { CostBreakdown } from "../types/api";
import { money } from "../utils";

export function CostCalculator({ breakdown, unitLabel }: { breakdown: CostBreakdown; unitLabel: string }) {
  const [quantity, setQuantity] = useState("1");
  const safeQuantity = Math.max(0, Number(quantity) || 0);

  const purchaseTotal = Number(breakdown.purchase_price_reference) * safeQuantity;
  const additionalTotal = Number(breakdown.total_additional_cost) * safeQuantity;
  const grandTotal = Number(breakdown.total_estimated_landing_storage_cost) * safeQuantity;

  return (
    <div className="cost-calculator">
      <div className="form-stack">
        <label>Quantity (each = {unitLabel})
          <input type="number" min="0" step="1" value={quantity} onChange={(e) => setQuantity(e.target.value)} />
        </label>
      </div>
      <dl className="data-list compact">
        <div><dt>Purchase cost</dt><dd>{money(purchaseTotal)}</dd></div>
        <div><dt>Additional costs (transport, storage, etc.)</dt><dd>{money(additionalTotal)}</dd></div>
        <div><dt>Estimated total</dt><dd><strong>{money(grandTotal)}</strong></dd></div>
      </dl>
    </div>
  );
}
