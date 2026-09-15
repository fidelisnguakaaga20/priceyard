import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate, useSearchParams } from "react-router-dom";
import { GoogleSignInButton } from "../components/GoogleSignInButton";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { PasswordField } from "../components/PasswordField";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export function RegisterPage() {
  const { register, loginWithGoogle, user } = useAuth();
  const navigate = useNavigate();
  const { showToast } = useToast();
  const [searchParams] = useSearchParams();
  const referralCode = (searchParams.get("ref") || "").trim().toUpperCase() || undefined;
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await register({ ...form, phone: form.phone || undefined, referral_code: referralCode });
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast("Registration successful. Welcome to PriceYard.");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast(err instanceof Error ? err.message : "Registration failed.", "error");
    }
  };

  const handleGoogleCredential = async (idToken: string) => {
    if (busy) return;
    setBusy(true);
    try {
      await loginWithGoogle(idToken);
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast("Welcome to PriceYard.");
      navigate("/dashboard", { replace: true });
    } catch (err) {
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast(err instanceof Error ? err.message : "Google sign-in failed.", "error");
    }
  };

  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">14-day trial</span><h1>Create your PriceYard account</h1><p>New normal users begin with the approved 14-day trial flow.</p>{referralCode && <p className="status-box">You were referred with code <strong>{referralCode}</strong> — the friend who shared it will get extra trial days once you register.</p>}<form className="form-stack" onSubmit={submit}><label>Full name<input required autoComplete="name" value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></label><label>Email<input type="email" required autoComplete="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Phone <small>(optional)</small><input autoComplete="tel" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label><label>Password <small>(minimum 8 characters)</small><PasswordField id="register-password" value={form.password} onChange={(password) => setForm({ ...form, password })} visible={showPassword} onToggle={() => setShowPassword((value) => !value)} autoComplete="new-password" minLength={8} maxLength={72} /></label><button className="button" disabled={busy}>{busy ? <ButtonSpinner label="Please wait…" /> : "Register"}</button></form><div className="auth-divider"><span>or</span></div><GoogleSignInButton onCredential={(token) => void handleGoogleCredential(token)} disabled={busy} /><p className="muted">Already registered? <Link className="text-link" to="/login">Log in</Link>.</p></div></section>;
}
