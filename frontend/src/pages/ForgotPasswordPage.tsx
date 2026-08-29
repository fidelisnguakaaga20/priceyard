import { FormEvent, useState } from "react";
import { Link } from "react-router-dom";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";

export function ForgotPasswordPage() {
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      const response = await apiFetch<{ message: string }>("/auth/forgot-password", { method: "POST", body: JSON.stringify({ email }) });
      setSent(true);
      showToast(response.message);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Password reset request failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">Account recovery</span><h1>Forgot your password?</h1><p>Enter your account email. If the account exists, PriceYard will send a secure reset link.</p>{sent ? <div className="status-box success">Check your email for the reset link. It expires after 15 minutes.</div> : <form className="form-stack" onSubmit={submit}><label>Email<input type="email" required autoComplete="email" value={email} onChange={(event) => setEmail(event.target.value)} /></label><button className="button" disabled={busy}>{busy ? <ButtonSpinner label="Please wait…" /> : "Send reset link"}</button></form>}<p className="muted"><Link className="text-link" to="/login">Return to login</Link>.</p></div></section>;
}
