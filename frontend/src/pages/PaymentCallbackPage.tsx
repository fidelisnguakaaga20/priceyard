import { useEffect, useState } from "react";
import { Link, useLocation } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useDocumentTitle } from "../hooks/useDocumentTitle";
import { apiFetch } from "../services/api";

export function PaymentCallbackPage() {
  const { token, refresh } = useAuth();
  const { search } = useLocation();
  const [confirmed, setConfirmed] = useState(false);
  useDocumentTitle(confirmed ? "Payment received" : "Payment");
  useEffect(() => {
    let current = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    const params = new URLSearchParams(search);
    const reference = params.get("reference") || params.get("trxref");
    const conflicts = params.get("reference") && params.get("trxref") && params.get("reference") !== params.get("trxref");
    setConfirmed(false);
    if (!token || !reference || reference.length > 100 || conflicts) return;
    const refreshAccount = refresh;
    const verify = async (attempt: number) => {
      try {
        const payment = await apiFetch<{ status: string }>(`/payments/${encodeURIComponent(reference)}/verify`, { method: "POST", keepalive: true }, token);
        if (payment.status === "success") {
          // A verification already in flight may finish after Go to Dashboard.
          // AuthContext ignores refreshes belonging to a superseded credential.
          await refreshAccount();
          if (current) setConfirmed(true);
          return;
        }
      } catch { /* Existing conditional support guidance remains visible. */ }
      if (current && attempt < 3) timer = setTimeout(() => { void verify(attempt+1); }, 2000);
    };
    void verify(0);
    return () => { current = false; clearTimeout(timer); };
    // Only a credential/reference change starts another bounded verification.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [token, search]);
  return (
    <section className="page page-section narrow">
      <div className="page-title">
        <span className="eyebrow">Payment</span>
        <h1>Thank you</h1>
        <p>
          If your payment was successful, your account will update within a few moments. If it does not update
          shortly, please contact support before trying again.
        </p>
      </div>
      <Link className="button" to="/dashboard">Go to Dashboard</Link>
    </section>
  );
}
