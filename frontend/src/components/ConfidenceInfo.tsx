import { useState } from "react";

const CONFIDENCE_DEFINITIONS: [string, string][] = [
  ["Reporter submitted", "A community reporter shared this price. Not yet independently verified."],
  ["Verified by 2 sources", "Two independent sources reported a similar price."],
  ["Admin confirmed", "A PriceYard admin personally confirmed this price."],
  ["Market visit confirmed", "Confirmed by an in-person market visit."],
  ["Low confidence", "Limited or conflicting information. Treat with extra caution."],
  ["Price outdated", "This price may no longer reflect current market conditions."],
];

export function ConfidenceInfo() {
  const [open, setOpen] = useState(false);
  return (
    <span className="confidence-info">
      <button type="button" className="confidence-info-toggle" aria-expanded={open} aria-label="What does confidence mean?" onClick={() => setOpen((value) => !value)}>?</button>
      {open && (
        <div className="confidence-info-popover" role="note">
          <ul>
            {CONFIDENCE_DEFINITIONS.map(([level, meaning]) => <li key={level}><strong>{level}:</strong> {meaning}</li>)}
          </ul>
          <button type="button" className="text-link confidence-info-close" onClick={() => setOpen(false)}>Close</button>
        </div>
      )}
    </span>
  );
}
