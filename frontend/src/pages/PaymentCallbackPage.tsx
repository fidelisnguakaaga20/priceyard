import { useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";

type PaymentStatus = { status: string; access_applied: boolean; requires_reconciliation: boolean };

export function PaymentCallbackPage() {
  useDocumentTitle("Payment status");
  const { token, refresh } = useAuth();
  const refreshRef = useRef(refresh);
  refreshRef.current = refresh;
  const [params] = useSearchParams();
  const reference = params.get("reference") || params.get("trxref") || "";
  const [message, setMessage] = useState("Checking your payment and account activation…");
  const [confirmed, setConfirmed] = useState(false);
  const [checking, setChecking] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    if (!token) return;
    if (!reference || reference.length > 128) {
      setMessage("A valid payment reference is missing. Check your dashboard or contact support with your receipt.");
      return;
    }
    let active = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const abort = new AbortController();
    let checks = 0;
    setChecking(true);
    async function check() {
      try {
        const payment = await apiFetch<PaymentStatus>(`/payments/status/${encodeURIComponent(reference)}`, { signal: abort.signal }, token);
        if (!active) return;
        if (payment.status === "success" && payment.access_applied) {
          await refreshRef.current();
          if (!active) return;
          setConfirmed(true);
          setMessage("Your payment is confirmed and your purchased access has been applied.");
          setChecking(false);
          return;
        }
        if (payment.requires_reconciliation) {
          setMessage("Your payment needs a support review. Keep your receipt and reference. Please do not pay again for the same purchase.");
          setChecking(false);
          return;
        }
        if (["failed", "abandoned"].includes(payment.status)) {
          setMessage("The payment has not been confirmed. If your bank account was charged, contact support with your receipt before trying again.");
          setChecking(false);
          return;
        }
        if (++checks < 12) { timer = setTimeout(() => void check(), 3000); return; }
        setMessage("Confirmation is still pending. Keep your receipt and reference; check again or contact support before paying again.");
      } catch (error) {
        if (!active) return;
        setMessage(error instanceof Error ? `Unable to confirm payment: ${error.message}. Keep your receipt and contact support before paying again.` : "Unable to confirm payment. Please contact support.");
      }
      if (active) setChecking(false);
    }
    void check();
    return () => { active = false; abort.abort(); if (timer) clearTimeout(timer); };
  }, [token, reference, attempt]);

  return <section className="page page-section narrow">
    <div className="page-title"><span className="eyebrow">Payment</span><h1>{confirmed ? "Access activated" : "Payment status"}</h1><p role="status" aria-live="polite">{message}</p></div>
    {reference && <p>Reference: <strong>{reference}</strong></p>}
    <div className="button-row">
      {!confirmed && <button className="button button-secondary" disabled={checking} onClick={() => setAttempt((value) => value + 1)}>{checking ? "Checking…" : "Check again"}</button>}
      <Link className="button" to="/dashboard">Go to Dashboard</Link>
    </div>
  </section>;
}
