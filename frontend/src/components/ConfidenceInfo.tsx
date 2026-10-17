import { useId, useRef, useState } from "react";

const CONFIDENCE_DEFINITIONS: [string, string][] = [
  ["Reporter submitted", "One person sent this price. Not checked yet."],
  ["Verified by 2 sources", "Two people said the same price."],
  ["Admin confirmed", "PriceYard staff checked this price."],
  ["Market visit confirmed", "Someone visited the market to check this price."],
  ["Low confidence", "Not sure about this price. Be careful."],
  ["Price outdated", "This price may be old now."],
];

export function ConfidenceInfo() {
  const [open, setOpen] = useState(false);
  const trigger = useRef<HTMLButtonElement>(null);
  const descriptionId = useId();
  const close = () => { setOpen(false); trigger.current?.focus(); };
  return (
    <span className="confidence-info" onKeyDown={event => { if (open && event.key === "Escape") { event.preventDefault(); event.stopPropagation(); close(); } }}>
      <button ref={trigger} type="button" className="confidence-info-toggle" aria-expanded={open} aria-controls={open ? descriptionId : undefined} aria-label="What does confidence mean?" onClick={() => setOpen((value) => !value)}>?</button>
      {open && (
        <div id={descriptionId} className="confidence-info-popover" role="note">
          <ul>
            {CONFIDENCE_DEFINITIONS.map(([level, meaning]) => <li key={level}><strong>{level}:</strong> {meaning}</li>)}
          </ul>
          <button type="button" className="text-link confidence-info-close" onClick={close}>Close</button>
        </div>
      )}
    </span>
  );
}
