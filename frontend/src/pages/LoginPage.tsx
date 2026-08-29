import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { PasswordField } from "../components/PasswordField";
import { useAuth } from "../context/AuthContext";
import { useToast } from "../context/ToastContext";

export function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const { showToast } = useToast();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;

  const submit = async (event: FormEvent) => {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    try {
      await login(email, password);
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast("Login successful. Welcome back to PriceYard.");
      navigate((location.state as { from?: string } | null)?.from || "/dashboard", { replace: true });
    } catch (err) {
      setBusy(false);
      await new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));
      showToast(err instanceof Error ? err.message : "Login failed.", "error");
    }
  };

  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">Account access</span><h1>Log in to PriceYard</h1><p>Use your account to check trial/paid access, watchlist and feedback.</p><form className="form-stack" onSubmit={submit}><label>Email<input type="email" required autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} /></label><label>Password<PasswordField id="login-password" value={password} onChange={setPassword} visible={showPassword} onToggle={() => setShowPassword((value) => !value)} autoComplete="current-password" maxLength={72} /></label><div className="auth-assist"><Link className="text-link" to="/forgot-password">Forgot password?</Link></div><button className="button" disabled={busy}>{busy ? <ButtonSpinner label="Please wait…" /> : "Log in"}</button></form><p className="muted">New to PriceYard? <Link className="text-link" to="/register">Create an account</Link>.</p></div></section>;
}
