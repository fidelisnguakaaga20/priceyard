import { useEffect, useState } from "react";

type LoadingSpinnerProps = {
  label?: string;
  size?: "small" | "medium" | "large";
};

const SLOW_LOAD_DELAY_MS = 4000;
const SLOW_LOAD_HINT = "Still loading — the server may be waking up, please wait…";

export function LoadingSpinner({ label = "Loading…", size = "medium" }: LoadingSpinnerProps) {
  const [slow, setSlow] = useState(false);
  useEffect(() => {
    setSlow(false);
    const timer = setTimeout(() => setSlow(true), SLOW_LOAD_DELAY_MS);
    return () => clearTimeout(timer);
  }, [label]);
  return (
    <div className="loading-indicator" role="status" aria-live="polite">
      <span className={`loading-spinner loading-spinner-${size}`} aria-hidden="true" />
      {label && <span className="loading-label">{slow ? SLOW_LOAD_HINT : label}</span>}
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
