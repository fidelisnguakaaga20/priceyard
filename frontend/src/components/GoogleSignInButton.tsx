import { useEffect, useId, useRef, useState } from "react";

type GoogleCredentialResponse = { credential: string };

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: { client_id: string; callback: (response: GoogleCredentialResponse) => void }) => void;
          renderButton: (parent: HTMLElement, options: { theme: string; size: string; width?: number; text?: string }) => void;
        };
      };
    };
  }
}

const CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID as string | undefined;
const SCRIPT_SRC = "https://accounts.google.com/gsi/client";

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

  useEffect(() => {
    if (!CLIENT_ID || disabled) return;
    let cancelled = false;
    loadGoogleScript()
      .then(() => {
        if (cancelled || !containerRef.current || !window.google) return;
        window.google.accounts.id.initialize({
          client_id: CLIENT_ID,
          callback: (response) => onCredential(response.credential),
        });
        containerRef.current.innerHTML = "";
        window.google.accounts.id.renderButton(containerRef.current, { theme: "outline", size: "large", text: "continue_with" });
      })
      .catch(() => { if (!cancelled) setError(true); });
    return () => { cancelled = true; };
  }, [disabled, onCredential]);

  if (!CLIENT_ID) return null;
  if (error) return <p className="muted">Google sign-in is unavailable right now.</p>;
  return <div id={containerId} ref={containerRef} className="google-signin-button" />;
}
