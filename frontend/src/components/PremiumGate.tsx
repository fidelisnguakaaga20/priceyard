import { Link } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function PremiumGate({ children }: { children: React.ReactNode }) {
  const { user, hasFullAccess, accessLabel } = useAuth();
  if (hasFullAccess) return <>{children}</>;
  return (
    <div className="locked-panel">
      <span className="lock-icon">🔒</span>
      <div>
        <strong>Full intelligence is locked for {accessLabel} access.</strong>
        <p>{user ? "Trial or active paid access is required for buying zones, sell-watch, storage suitability and cost breakdown." : "Log in to check your PriceYard access level."}</p>
        {!user && <Link className="button button-small" to="/login">Log in</Link>}
      </div>
    </div>
  );
}
