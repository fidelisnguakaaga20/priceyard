import { Link } from "react-router-dom";
import type { ToastAction } from "../context/ToastContext";

export type ToastKind = "success" | "error";

type ToastProps = {
  kind: ToastKind;
  message: string;
  action?: ToastAction;
  onDismiss: () => void;
};

export function Toast({ kind, message, action, onDismiss }: ToastProps) {
  return (
    <div className="toast-region" aria-live="polite" aria-atomic="true">
      <div className={`toast toast-${kind}`} role={kind === "error" ? "alert" : "status"}>
        <span className="toast-icon" aria-hidden="true">{kind === "success" ? "✓" : "!"}</span>
        <span className="toast-message">
          {message}
          {action && <Link className="toast-action" to={action.to} onClick={onDismiss}>{action.label}</Link>}
        </span>
        <button className="toast-dismiss" type="button" onClick={onDismiss} aria-label="Dismiss message">×</button>
      </div>
    </div>
  );
}
