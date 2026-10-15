import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function PremiumGate({ children }: { children: React.ReactNode }) {
  const { user, hasFullAccess } = useAuth();
  if (hasFullAccess) return <>{children}</>;
  return (
    <div className="locked-panel">
      <span className="lock-icon">🔒</span>
      <div>
        <strong>This information is locked.</strong>
        <p>{user ? "Upgrade to see this." : "Register for a 14-day trial, or log in if you already have access."}</p>
        <Link className="button button-small" to={user ? "/dashboard" : "/login"}>{user ? "Upgrade →" : "Log in"}</Link>
      </div>
    </div>
  );
}
