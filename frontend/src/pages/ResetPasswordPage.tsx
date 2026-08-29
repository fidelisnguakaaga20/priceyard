import { FormEvent, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { PasswordField } from "../components/PasswordField";
import { useToast } from "../context/ToastContext";
import { apiFetch } from "../services/api";

export function ResetPasswordPage() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";
  const { showToast } = useToast();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [busy, setBusy] = useState(false);
  const [complete, setComplete] = useState(false);

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    if (password !== confirmPassword) {
      showToast("Passwords do not match.", "error");
      return;
    }
    setBusy(true);
    try {
      const response = await apiFetch<{ message: string }>("/auth/reset-password", { method: "POST", body: JSON.stringify({ token, new_password: password }) });
      setComplete(true);
      showToast(response.message);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Password reset failed.", "error");
    } finally {
      setBusy(false);
    }
  };

  if (!token) return <section className="page auth-page"><div className="auth-card"><h1>Invalid reset link</h1><p>This password reset link is incomplete.</p><Link className="text-link" to="/forgot-password">Request a new link</Link>.</div></section>;
  if (complete) return <section className="page auth-page"><div className="auth-card"><h1>Password updated</h1><div className="status-box success">Your password was reset successfully.</div><Link className="button" to="/login">Log in</Link></div></section>;

  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">Secure reset</span><h1>Create a new password</h1><p>Use at least 8 characters. This reset link works only once.</p><form className="form-stack" onSubmit={submit}><label>New password<PasswordField id="reset-password" value={password} onChange={setPassword} visible={showPassword} onToggle={() => setShowPassword((value) => !value)} autoComplete="new-password" minLength={8} maxLength={72} /></label><label>Confirm new password<PasswordField id="confirm-reset-password" value={confirmPassword} onChange={setConfirmPassword} visible={showConfirmation} onToggle={() => setShowConfirmation((value) => !value)} autoComplete="new-password" minLength={8} maxLength={72} /></label><button className="button" disabled={busy}>{busy ? <ButtonSpinner label="Please wait…" /> : "Reset password"}</button></form></div></section>;
}
