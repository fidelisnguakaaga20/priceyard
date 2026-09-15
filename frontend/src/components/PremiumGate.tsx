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
        <p>{user ? "You need active trial or paid access to see buying zones, sell-watch, storage tips and cost breakdown." : "Register free or log in to unlock full price details."}</p>
        {!user && <Link className="button button-small" to="/login">Log in</Link>}
      </div>
    </div>
  );
}
