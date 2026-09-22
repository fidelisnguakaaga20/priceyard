import { useEffect, useRef } from "react";
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
  const timeoutRef = useRef<number | null>(null);
  const duration = action ? 8000 : 4500;

  const stopTimer = () => {
    if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
  };
  const startTimer = () => {
    stopTimer();
    timeoutRef.current = window.setTimeout(onDismiss, duration);
  };

  useEffect(() => {
    startTimer();
    return stopTimer;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [message, kind]);

  return (
    <div className="toast-region" aria-live="polite" aria-atomic="true">
      <div
        className={`toast toast-${kind}`}
        role={kind === "error" ? "alert" : "status"}
        onMouseEnter={stopTimer}
        onMouseLeave={startTimer}
        onFocus={stopTimer}
        onBlur={startTimer}
      >
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
