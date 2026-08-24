import { FormEvent, useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { ButtonSpinner } from "../components/LoadingSpinner";
import { useAuth } from "../context/AuthContext";

export function RegisterPage() {
  const { register, user } = useAuth(); const navigate = useNavigate();
  const [form, setForm] = useState({ full_name: "", email: "", phone: "", password: "" }); const [error, setError] = useState(""); const [busy, setBusy] = useState(false);
  if (user) return <Navigate to="/dashboard" replace />;
  const submit = async (event: FormEvent) => { event.preventDefault(); setBusy(true); setError(""); try { await register({ ...form, phone: form.phone || undefined }); navigate("/dashboard", { replace: true }); } catch (err) { setError((err as Error).message); } finally { setBusy(false); } };
  return <section className="page auth-page"><div className="auth-card"><span className="eyebrow">14-day trial</span><h1>Create your PriceYard account</h1><p>New normal users begin with the approved 14-day trial flow.</p><form className="form-stack" onSubmit={submit}><label>Full name<input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} /></label><label>Email<input type="email" required value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label><label>Phone <small>(optional)</small><input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label><label>Password<input type="password" required value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} /></label>{error && <div className="status-box error">{error}</div>}<button className="button" disabled={busy}>{busy ? <ButtonSpinner label="Please wait…" /> : "Register"}</button></form><p className="muted">Already registered? <Link className="text-link" to="/login">Log in</Link>.</p></div></section>;
}
