import { useState } from "react";

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

  const finish = () => {
    setDismissed(true);
    try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* ignore */ }
    window.dispatchEvent(new Event(ONBOARDING_TOUR_SEEN_EVENT));
  };

  if (dismissed) return null;

  const isLast = step === STEPS.length - 1;
  const isFirst = step === 0;

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-label="Welcome to PriceYard">
      <div className="onboarding-card">
        <span className="eyebrow">Welcome to PriceYard ({step + 1}/{STEPS.length})</span>
        <p>{STEPS[step]}</p>
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
