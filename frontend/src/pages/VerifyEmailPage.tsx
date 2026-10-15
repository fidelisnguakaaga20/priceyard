import { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { apiFetch } from "../services/api";
import { useAuth } from "../context/AuthContext";

export function VerifyEmailPage() {
  const [params] = useSearchParams();
  const { refresh } = useAuth();
  const [message, setMessage] = useState("");
  const [busy, setBusy] = useState(false);
  async function verify() {
    setBusy(true);
    try {
      await apiFetch("/auth/verify-email", { method: "POST", body: JSON.stringify({ token: params.get("token") || "" }) });
      setMessage("Email verified. Your existing trial and purchased access are unchanged.");
      await refresh();
    } catch (error) { setMessage((error as Error).message); }
    finally { setBusy(false); }
  }
  return <section className="page page-section narrow"><h1>Verify your email</h1>
    <p>Confirm ownership of your email to link sign-in methods and qualify referrals.</p>
    <button className="button" disabled={busy || !params.get("token")} onClick={() => void verify()}>{busy ? "Verifying…" : "Verify email"}</button>
    {message && <p role="status">{message}</p>}<Link to="/dashboard">Return to your account</Link></section>;
}
