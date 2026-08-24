export type ToastKind = "success" | "error";

type ToastProps = {
  kind: ToastKind;
  message: string;
  onDismiss: () => void;
};

export function Toast({ kind, message, onDismiss }: ToastProps) {
  return (
    <div className="toast-region" aria-live="polite" aria-atomic="true">
      <div className={`toast toast-${kind}`} role={kind === "error" ? "alert" : "status"}>
        <span className="toast-icon" aria-hidden="true">{kind === "success" ? "✓" : "!"}</span>
        <span className="toast-message">{message}</span>
        <button className="toast-dismiss" type="button" onClick={onDismiss} aria-label="Dismiss message">×</button>
      </div>
    </div>
  );
}
