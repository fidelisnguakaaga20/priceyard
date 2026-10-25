import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { Link } from "react-router-dom";
import { ONBOARDING_TOUR_SEEN_EVENT, ONBOARDING_TOUR_SEEN_KEY } from "../components/OnboardingTour";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";
import type { PaymentInitiateResponse, PaymentPlan, ReferralSummary, SubmissionStats } from "../types/api";
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
  const [submissionStats, setSubmissionStats] = useState<SubmissionStats | null>(null);
  const [copied, setCopied] = useState(false);
  const [upgrading, setUpgrading] = useState<PaymentPlan | null>(null);
  const accountKey = `${token ?? ""}:${user?.id ?? ""}:${user?.role ?? ""}`;
  const activeAccount = useRef<string | null>(accountKey);
  const pendingCheckout = useRef<AbortController | null>(null);
  const checkoutBusy = useRef(false);
  const copiedTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  activeAccount.current = accountKey;
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
  useLayoutEffect(() => {
    activeAccount.current = accountKey;
    setReferral(null);
    setSubmissionStats(null);
    setCopied(false);
    setUpgrading(null);
    checkoutBusy.current = false;
    const controller = new AbortController();
    const current = () => !controller.signal.aborted && activeAccount.current === accountKey;
    if (token && user && user.role !== "admin") {
      void apiFetch<ReferralSummary>("/auth/referral-summary", { signal: controller.signal }, token)
        .then((data) => { if (current()) setReferral(data); }).catch(() => undefined);
      if (user.role === "reporter") {
        void apiFetch<SubmissionStats>("/price-updates/my-stats", { signal: controller.signal }, token)
          .then((data) => { if (current()) setSubmissionStats(data); }).catch(() => undefined);
      }
    }
    return () => {
      activeAccount.current = null;
      controller.abort();
      pendingCheckout.current?.abort();
      pendingCheckout.current = null;
      if (copiedTimer.current !== null) clearTimeout(copiedTimer.current);
      copiedTimer.current = null;
    };
  }, [accountKey]);
  const copyReferralLink = async () => {
    if (!referral || activeAccount.current !== accountKey) return;
    try {
      await navigator.clipboard.writeText(referralLink(referral.referral_code));
      if (activeAccount.current !== accountKey) return;
      setCopied(true);
      if (copiedTimer.current !== null) clearTimeout(copiedTimer.current);
      copiedTimer.current = setTimeout(() => {
        if (activeAccount.current === accountKey) setCopied(false);
        copiedTimer.current = null;
      }, 2000);
    } catch { /* clipboard unavailable */ }
  };
  const startUpgrade = async (plan: PaymentPlan) => {
    if (!token || upgrading || checkoutBusy.current || activeAccount.current !== accountKey) return;
    checkoutBusy.current = true;
    const controller = new AbortController();
    pendingCheckout.current = controller;
    const current = () => !controller.signal.aborted && activeAccount.current === accountKey && pendingCheckout.current === controller;
    setUpgrading(plan);
    try {
      const result = await apiFetch<PaymentInitiateResponse>("/payments/initiate", { method: "POST", body: JSON.stringify({ plan }), signal: controller.signal }, token);
      if (!current()) return;
      window.location.href = result.authorization_url;
    } catch (err) {
      if (!current()) return;
      showToast((err as Error).message || "Could not start payment.", "error");
      setUpgrading(null);
      checkoutBusy.current = false;
    } finally {
      if (pendingCheckout.current === controller) pendingCheckout.current = null;
    }
  };
  if (!user) return null;
  const showUpgrade = user.role !== "admin" && subscription?.status !== "active";
  return <section className="page page-section"><div className="page-title"><span className="eyebrow">User dashboard</span><h1>Welcome, {user.full_name}</h1><p>Your account and quick links to PriceYard tools.</p></div>
    {user.role !== "admin" && !onboardingDismissed && tourSeen && (
      <article className="card onboarding-card dashboard-onboarding-card">
        <div className="card-row">
          <div><span className="onboarding-heading">New here?</span><h2>Get started with PriceYard</h2></div>
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
    {submissionStats && (
      <article className="card">
        <span className="eyebrow">Your field reports</span>
        <h2>{submissionStats.submitted} submitted</h2>
        <p>Thanks for helping keep PriceYard current. Every report is reviewed by an admin before it goes live.</p>
        <dl className="data-list compact">
          <div><dt>Approved</dt><dd>{submissionStats.approved}</dd></div>
          <div><dt>Pending review</dt><dd>{submissionStats.pending}</dd></div>
          <div><dt>Rejected</dt><dd>{submissionStats.rejected}</dd></div>
        </dl>
        <div className="button-row"><Link className="button button-small" to="/report-price">Report another price →</Link></div>
      </article>
    )}
    {referral && (
      <article className="card">
        <span className="eyebrow">Invite a friend</span>
        <h2>Get {referral.reward_days} extra trial days per referral</h2>
        <p>Share your link. While you have free access or an active trial, each registration can add {referral.reward_days} trial days, up to 3 bonuses in any 30 days. Existing earned days stay yours.</p>
        <dl className="data-list compact"><div><dt>Your referral code</dt><dd>{referral.referral_code}</dd></div><div><dt>People referred so far</dt><dd>{referral.referred_count}</dd></div></dl>
        <div className="button-row">
          <button type="button" className="button button-small button-secondary" onClick={() => void copyReferralLink()}>{copied ? "Link copied!" : "Copy referral link"}</button>
          <a className="button button-small" href={referralWhatsAppShareUrl(referral.referral_code, referral.reward_days)} target="_blank" rel="noopener noreferrer">Share on WhatsApp</a>
        </div>
      </article>
    )}
    <div className="shortcut-grid"><Link className="shortcut" to="/prices"><strong>Prices</strong><span>See latest prices →</span></Link><Link className="shortcut" to="/watchlist"><strong>Watchlist</strong><span>See what you saved →</span></Link><Link className="shortcut" to="/feedback"><strong>Feedback</strong><span>Tell us what you think →</span></Link><Link className="shortcut" to="/history"><strong>History</strong><span>See past prices →</span></Link>{(user.role === "reporter" || user.role === "admin") && <Link className="shortcut" to="/report-price"><strong>Report a price</strong><span>Submit a field observation →</span></Link>}{user.role === "admin" && <Link className="shortcut" to="/admin"><strong>Admin</strong><span>Manage PriceYard MVP records →</span></Link>}</div>
  </section>;
}
