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
        <p>{user ? "Upgrade to see this." : "Register free or log in to unlock full price details."}</p>
        <Link className="button button-small" to={user ? "/dashboard" : "/login"}>{user ? "Upgrade →" : "Log in"}</Link>
      </div>
    </div>
  );
}
