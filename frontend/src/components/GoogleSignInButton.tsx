import { useEffect, useId, useRef, useState } from "react";

type GoogleCredentialResponse = { credential: string };

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: GoogleCredentialResponse) => void; use_fedcm_for_prompt?: boolean }) => void;
          renderButton: (parent: HTMLElement, options: { theme: string; size: string; width?: number; text?: string }) => void;
        };
      };
    };
  }
}

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
const SCRIPT_SRC = "https://accounts.google.com/gsi/client";
const STUCK_HINT_DELAY_MS = 3000;

let scriptLoadPromise: Promise<void> | null = null;
function loadGoogleScript(): Promise<void> {
  if (window.google?.accounts?.id) return Promise.resolve();
  if (!scriptLoadPromise) {
    scriptLoadPromise = new Promise((resolve, reject) => {
      const script = document.createElement("script");
      script.src = SCRIPT_SRC;
      script.async = true;
      script.onload = () => resolve();
      script.onerror = () => reject(new Error("Failed to load Google sign-in"));
      document.head.appendChild(script);
    });
  }
  return scriptLoadPromise;
}

export function GoogleSignInButton({ onCredential, disabled }: { onCredential: (idToken: string) => void; disabled?: boolean }) {
  const containerId = useId();
  const containerRef = useRef<HTMLDivElement>(null);
  const [error, setError] = useState(false);
  const [showStuckHint, setShowStuckHint] = useState(false);
  const completedRef = useRef(false);

  useEffect(() => {
    if (!CLIENT_ID || disabled) return;
    let cancelled = false;
    loadGoogleScript()
      .then(() => {
        if (cancelled || !containerRef.current || !window.google) return;
        window.google.accounts.id.initialize({
          client_id: CLIENT_ID,
          use_fedcm_for_prompt: true,
          callback: (response) => { completedRef.current = true; onCredential(response.credential); },
        });
        containerRef.current.innerHTML = "";
        window.google.accounts.id.renderButton(containerRef.current, { theme: "outline", size: "large", text: "continue_with" });
      })
      .catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [disabled, onCredential]);

  // The Google button opens its own popup/tab for sign-in, which occasionally loads blank
  // (a known flakiness in Google's popup fallback, not something this app controls). A window
  // blur followed by a focus return with no credential received means the user left and came
  // back without finishing -- e.g. they gave up on a stuck popup -- so we surface a fallback hint.
  useEffect(() => {
    if (!CLIENT_ID || disabled) return;
    let blurredAt: number | null = null;
    const onBlur = () => { blurredAt = Date.now(); };
    const onFocus = () => {
      if (blurredAt !== null && !completedRef.current && Date.now() - blurredAt > STUCK_HINT_DELAY_MS) {
        setShowStuckHint(true);
      }
      blurredAt = null;
    };
    window.addEventListener("blur", onBlur);
    window.addEventListener("focus", onFocus);
    return () => {
      window.removeEventListener("blur", onBlur);
      window.removeEventListener("focus", onFocus);
    };
  }, [disabled]);

  if (!CLIENT_ID) return null;
  if (error) return <p className="muted">Google sign-in is unavailable right now.</p>;
  return (
    <div>
      <div id={containerId} ref={containerRef} className="google-signin-button" />
      {showStuckHint && <p className="muted">Google sign-in stuck or blank? Try again, or use email and password below.</p>}
    </div>
  );
}
