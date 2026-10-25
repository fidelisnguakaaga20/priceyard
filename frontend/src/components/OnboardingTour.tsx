import { useEffect, useRef, useState } from "react";

export const ONBOARDING_TOUR_SEEN_KEY = "priceyard_onboarding_seen";
export const ONBOARDING_TOUR_SEEN_EVENT = "priceyard-onboarding-seen";
const SEEN_KEY = ONBOARDING_TOUR_SEEN_KEY;

const STEPS = [
  "We show you a low price and a high price, not just one price — because that is how the real market works.",
  "Every price has a label that tells you how sure we are. Some are just reported. Some are confirmed by someone who visited the market.",
  "Free users see today's prices. Trial and Paid users also see old prices, best time to buy, best time to sell, and storage tips.",
  "Save any product or market you like. We will email you when the price changes, so you don't have to keep checking.",
];

export function OnboardingTour() {
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(SEEN_KEY) === "1"; } catch { return true; }
  });
  const [step, setStep] = useState(0);
  const dialog = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (dismissed) return;
    const previous = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    dialog.current?.querySelector<HTMLButtonElement>("button")?.focus();
    return () => {
      const target = previous?.isConnected && previous !== document.body ? previous : document.querySelector<HTMLElement>(".brand");
      target?.focus();
    };
  }, [dismissed]);

  useEffect(() => {
    // Back can remove the focused control on the first step. Keep keyboard
    // focus inside the dialog so Tab and Escape continue to work.
    if (!dismissed && dialog.current && !dialog.current.contains(document.activeElement)) {
      dialog.current.querySelector<HTMLButtonElement>("button")?.focus();
    }
  }, [dismissed, step]);

  const finish = () => {
    setDismissed(true);
    try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* ignore */ }
    window.dispatchEvent(new Event(ONBOARDING_TOUR_SEEN_EVENT));
  };

  if (dismissed) return null;

  const isLast = step === STEPS.length - 1;
  const isFirst = step === 0;

  return (
    <div ref={dialog} className="onboarding-overlay" role="dialog" aria-modal="true" aria-label="Welcome to PriceYard" aria-describedby="priceyard-onboarding-step" onKeyDown={event => {
      if (event.key === "Escape") { event.preventDefault(); finish(); return; }
      if (event.key !== "Tab") return;
      const controls = Array.from(event.currentTarget.querySelectorAll<HTMLButtonElement>("button:not(:disabled)"));
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    }}>
      <div className="onboarding-card">
        <h2 className="onboarding-heading">Welcome to PriceYard ({step + 1}/{STEPS.length})</h2>
        <p id="priceyard-onboarding-step" aria-live="polite">{STEPS[step]}</p>
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
