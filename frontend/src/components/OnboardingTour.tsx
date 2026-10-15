import { useCallback, useEffect, useRef, useState } from "react";

export const ONBOARDING_TOUR_SEEN_KEY = "priceyard_onboarding_seen";
export const ONBOARDING_TOUR_SEEN_EVENT = "priceyard-onboarding-seen";
const SEEN_KEY = ONBOARDING_TOUR_SEEN_KEY;

const STEPS = [
  "We show you a low price and a high price, not just one price — because that is how the real market works.",
  "Every price has a label that tells you how sure we are. Some are just reported. Some are confirmed by someone who visited the market.",
  "Free users see current price summaries. Trial and Paid users also see price history, buying and selling observations, and storage information.",
  "Save a product or market to follow its approved prices. You can receive available price alerts and set a target for a confirmed measurement.",
];

export function OnboardingTour() {
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(SEEN_KEY) === "1"; } catch { return true; }
  });
  const [step, setStep] = useState(0);
  const dialog = useRef<HTMLDivElement>(null);

  const finish = useCallback(() => {
    setDismissed(true);
    try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* ignore */ }
    window.dispatchEvent(new Event(ONBOARDING_TOUR_SEEN_EVENT));
  }, []);

  useEffect(() => {
    if (dismissed || !dialog.current) return;
    const element = dialog.current;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    const previousOverflow = document.body.style.overflow;
    document.body.style.overflow = "hidden";
    const buttons = () => Array.from(element.querySelectorAll<HTMLElement>('button:not([disabled]), a[href], input:not([disabled]), select:not([disabled]), [tabindex="0"]'));
    const focusFirst = () => (buttons()[0] || element).focus();
    focusFirst();
    const keyboard = (event: KeyboardEvent) => {
      if (event.key === "Escape") { event.preventDefault(); finish(); return; }
      if (event.key !== "Tab") return;
      const targets = buttons();
      const first = targets[0];
      const last = targets[targets.length - 1];
      if (!first) { event.preventDefault(); element.focus(); }
      else if (event.shiftKey && (document.activeElement === first || !element.contains(document.activeElement))) { event.preventDefault(); last.focus(); }
      else if (!event.shiftKey && (document.activeElement === last || !element.contains(document.activeElement))) { event.preventDefault(); first.focus(); }
    };
    const maintainFocus = (event: FocusEvent) => { if (!element.contains(event.target as Node)) focusFirst(); };
    document.addEventListener("keydown", keyboard);
    document.addEventListener("focusin", maintainFocus);
    return () => {
      document.removeEventListener("keydown", keyboard);
      document.removeEventListener("focusin", maintainFocus);
      document.body.style.overflow = previousOverflow;
      if (previous?.isConnected) previous.focus();
    };
  }, [dismissed, finish]);

  if (dismissed) return null;

  const isLast = step === STEPS.length - 1;
  const isFirst = step === 0;

  return (
    <div className="onboarding-overlay" ref={dialog} tabIndex={-1} role="dialog" aria-modal="true" aria-label="Welcome to PriceYard" aria-describedby="onboarding-instruction">
      <div className="onboarding-card">
        <span className="eyebrow">Welcome to PriceYard ({step + 1}/{STEPS.length})</span>
        <p id="onboarding-instruction" aria-live="polite">{STEPS[step]}</p>
        <div className="onboarding-actions">
          <button type="button" className="text-link text-link-button" onClick={finish}>Skip</button>
          <div className="onboarding-nav-buttons">
            {!isFirst && <button type="button" className="button button-secondary button-small" onClick={() => setStep((s) => s - 1)}>Back</button>}
            <button type="button" className="button button-small" onClick={() => (isLast ? finish() : setStep((s) => s + 1))}>{isLast ? "Got it" : "Next"}</button>
          </div>
        </div>
      </div>
    </div>
  );
}
