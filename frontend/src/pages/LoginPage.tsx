import { FormEvent, useState } from "react";
import { Link, Navigate, useLocation, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function LoginPage() {
  const { login, user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [email, setEmail] = useState(""); const [password, setPassword] = useState(""); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;
  const submit = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { await login(email, password); const target = (location.state as { from?: string } | null)?.from || "/dashboard"; navigate(target, { replace: true }); } catch (err) { setError((err as Error).message); } finally { setBusy(false); } };
  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">Account access</span><h1>Log in to PriceYard</h1><p>Use your account to check trial/paid access, watchlist and feedback.</p><form className="form-stack" onSubmit={submit}><label>Email<input type="email" required value={email} onChange={(e) => setEmail(e.target.value)} /></label><label>Password<input type="password" required value={password} onChange={(e) => setPassword(e.target.value)} /></label>{error && <div className="status-box error">{error}</div>}<button className="button" disabled={busy}>{busy ? "Logging in…" : "Log in"}</button></form><p className="muted">New to PriceYard? <Link className="text-link" to="/register">Create an account</Link>.</p></div></section>;
}
