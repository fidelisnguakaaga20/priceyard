type LoadingSpinnerProps = {
  label?: string;
  size?: "small" | "medium" | "large";
};

export function LoadingSpinner({ label = "Loading…", size = "medium" }: LoadingSpinnerProps) {
  return (
    <div className="loading-indicator" role="status" aria-live="polite">
      <span className={`loading-spinner loading-spinner-${size}`} aria-hidden="true" />
      {label && <span className="loading-label">{label}</span>}
    </div>
  );
}

export function FullPageLoader({ label = "Please wait…", dark = false }: { label?: string; dark?: boolean }) {
  return (
    <div className={`loading-overlay ${dark ? "loading-overlay-dark" : "loading-overlay-light"}`}>
      <LoadingSpinner label={label} size="large" />
    </div>
  );
}

export function ButtonSpinner({ label = "Please wait…" }: { label?: string }) {
  return (
    <span className="button-loading-content" role="status" aria-live="polite">
      <span className="button-spinner" aria-hidden="true" />
      <span>{label}</span>
    </span>
  );
}
