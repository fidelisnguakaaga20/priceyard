import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { ONBOARDING_TOUR_SEEN_EVENT, ONBOARDING_TOUR_SEEN_KEY } from "../components/OnboardingTour";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";
import type { PaymentInitiateResponse, PaymentPlan, ReferralSummary } from "../types/api";
import { dateOnly, referralLink, referralWhatsAppShareUrl } from "../utils";

const ONBOARDING_KEY = "priceyard_onboarding_dismissed";

function readOnboardingDismissed(): boolean {
  try { return localStorage.getItem(ONBOARDING_KEY) === "1"; } catch { return false; }
}

function readTourSeen(): boolean {
  try { return localStorage.getItem(ONBOARDING_TOUR_SEEN_KEY) === "1"; } catch { return false; }
}

export function DashboardPage() {
  const { user, subscription, accessLabel, hasFullAccess, token } = useAuth();
  const { showToast } = useToast();
  const [onboardingDismissed, setOnboardingDismissed] = useState(readOnboardingDismissed);
  const [tourSeen, setTourSeen] = useState(readTourSeen);
  const [referral, setReferral] = useState<ReferralSummary | null>(null);
  const [copied, setCopied] = useState(false);
  const [upgrading, setUpgrading] = useState<PaymentPlan | null>(null);
  const dismissOnboarding = () => {
    try { localStorage.setItem(ONBOARDING_KEY, "1"); } catch { /* ignore storage failures */ }
    setOnboardingDismissed(true);
  };
  useEffect(() => {
    if (tourSeen) return;
    const onSeen = () => setTourSeen(true);
    window.addEventListener(ONBOARDING_TOUR_SEEN_EVENT, onSeen);
    return () => window.removeEventListener(ONBOARDING_TOUR_SEEN_EVENT, onSeen);
  }, [tourSeen]);
  useEffect(() => {
    if (!token || user?.role === "admin") return;
    apiFetch<ReferralSummary>("/auth/referral-summary", {}, token).then(setReferral).catch(() => undefined);
  }, [token, user?.role]);
  const copyReferralLink = async () => {
    if (!referral) return;
    try {
      await navigator.clipboard.writeText(referralLink(referral.referral_code));
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch { /* clipboard unavailable */ }
  };
  const startUpgrade = async (plan: PaymentPlan) => {
    if (!token || upgrading) return;
    setUpgrading(plan);
    try {
      const result = await apiFetch<PaymentInitiateResponse>("/payments/initiate", { method: "POST", body: JSON.stringify({ plan }) }, token);
      window.location.href = result.authorization_url;
    } catch (err) {
      showToast((err as Error).message || "Could not start payment.", "error");
      setUpgrading(null);
    }
  };
  if (!user) return null;
  const showUpgrade = user.role !== "admin" && subscription?.status !== "active";
  return <section className="page page-section"><div className="page-title"><span className="eyebrow">User dashboard</span><h1>Welcome, {user.full_name}</h1><p>Your account and quick links to PriceYard tools.</p></div>
    {user.role !== "admin" && !onboardingDismissed && tourSeen && (
      <article className="card onboarding-card">
        <div className="card-row">
          <div><span className="eyebrow">New here?</span><h2>Get started with PriceYard</h2></div>
          <button className="button button-small button-secondary" type="button" onClick={dismissOnboarding}>Dismiss</button>
        </div>
        <ul className="onboarding-list">
          <li><Link to="/prices">Check current prices →</Link> See today's approved ranges for Egusi and more.</li>
          <li><Link to="/watchlist">Save your first watchlist item →</Link> Build a personal shortlist of what you track.</li>
          <li><Link to="/faq">Read the FAQ →</Link> Understand confidence levels, disclaimers and how prices are verified.</li>
        </ul>
      </article>
    )}
    <div className="dashboard-grid">
      <article className="card"><span className="eyebrow">Current access</span><h2>{accessLabel}</h2><p>{hasFullAccess ? "You can see full price details." : "You have limited access. Start a trial or upgrade to see everything."}</p>{user.role !== "admin" && subscription && <dl className="data-list compact"><div><dt>Status</dt><dd>{subscription.status}</dd></div><div><dt>Trial ends</dt><dd>{dateOnly(subscription.trial_ends_at)}</dd></div><div><dt>Plan</dt><dd>{subscription.plan_name}</dd></div></dl>}</article>
      <article className="card"><span className="eyebrow">Account</span><h2>{user.email}</h2><p>Role: {user.role.replace(/_/g, " ")}</p></article>
    </div>
    {showUpgrade && (
      <article className="card">
        <span className="eyebrow">Upgrade</span>
        <h2>Get full access</h2>
        <p>See buying zones, sell-watch windows, storage suitability and cost breakdowns for every commodity, with no trial limits.</p>
        <div className="button-row">
          <button type="button" className="button" disabled={upgrading !== null} onClick={() => void startUpgrade("monthly")}>{upgrading === "monthly" ? "Please wait…" : "₦2,500 / month"}</button>
          <button type="button" className="button button-secondary" disabled={upgrading !== null} onClick={() => void startUpgrade("seasonal")}>{upgrading === "seasonal" ? "Please wait…" : "₦6,000 / 3 months"}</button>
        </div>
      </article>
    )}
    {referral && (
      <article className="card">
        <span className="eyebrow">Invite a friend</span>
        <h2>Get {referral.reward_days} extra trial days per referral</h2>
        <p>Share your link. When someone registers with it, you get {referral.reward_days} extra trial days automatically.</p>
        <dl className="data-list compact"><div><dt>Your referral code</dt><dd>{referral.referral_code}</dd></div><div><dt>People referred so far</dt><dd>{referral.referred_count}</dd></div></dl>
        <div className="button-row">
          <button type="button" className="button button-small button-secondary" onClick={() => void copyReferralLink()}>{copied ? "Link copied!" : "Copy referral link"}</button>
          <a className="button button-small" href={referralWhatsAppShareUrl(referral.referral_code, referral.reward_days)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
        </div>
      </article>
    )}
    <div className="shortcut-grid"><Link className="shortcut" to="/prices"><strong>Prices</strong><span>See latest prices →</span></Link><Link className="shortcut" to="/watchlist"><strong>Watchlist</strong><span>See what you saved →</span></Link><Link className="shortcut" to="/feedback"><strong>Feedback</strong><span>Tell us what you think →</span></Link><Link className="shortcut" to="/history"><strong>History</strong><span>See past prices →</span></Link>{user.role === "admin" && <Link className="shortcut" to="/admin"><strong>Admin</strong><span>Manage PriceYard MVP records →</span></Link>}</div>
  </section>;
}
