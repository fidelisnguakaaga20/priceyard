import { useState } from "react";

const SEEN_KEY = "priceyard_onboarding_seen";

const STEPS = [
  "PriceYard shows real market prices as a range, not one fixed number — because real markets don't work with a single price.",
  "Confidence labels tell you how sure we are about a price, from \"Reporter submitted\" to \"Market visit confirmed\".",
  "Free access shows today's prices. Trial and Paid unlock price history, buying zones, sell-watch windows, and storage advice.",
  "Save any commodity or market to your Watchlist and we'll email you when the price changes — no need to keep checking back.",
];

export function OnboardingTour() {
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(SEEN_KEY) === "1"; } catch { return true; }
  });
  const [step, setStep] = useState(0);

  const finish = () => {
    setDismissed(true);
    try { localStorage.setItem(SEEN_KEY, "1"); } catch { /* ignore */ }
  };

  if (dismissed) return null;

  const isLast = step === STEPS.length - 1;

  return (
    <div className="onboarding-overlay" role="dialog" aria-modal="true" aria-label="Welcome to PriceYard">
      <div className="onboarding-card">
        <span className="eyebrow">Welcome to PriceYard ({step + 1}/{STEPS.length})</span>
        <p>{STEPS[step]}</p>
        <div className="onboarding-actions">
          <button type="button" className="text-link text-link-button" onClick={finish}>Skip</button>
          <button type="button" className="button button-small" onClick={() => (isLast ? finish() : setStep((s) => s + 1))}>{isLast ? "Got it" : "Next"}</button>
        </div>
      </div>
    </div>
  );
}
