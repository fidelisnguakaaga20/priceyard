import { useEffect, useState } from "react";

const DISMISS_KEY = "priceyard_install_dismissed";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed" }>;
};

function isStandalone(): boolean {
  try {
    return (
      window.matchMedia("(display-mode: standalone)").matches ||
      (window.navigator as unknown as { standalone?: boolean }).standalone === true
    );
  } catch {
    return false;
  }
}

function isIos(): boolean {
  return /iphone|ipad|ipod/i.test(window.navigator.userAgent);
}

export function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null);
  const [showIosHelp, setShowIosHelp] = useState(false);
  const [dismissed, setDismissed] = useState(() => {
    try { return localStorage.getItem(DISMISS_KEY) === "1"; } catch { return false; }
  });

  useEffect(() => {
    if (dismissed || isStandalone()) return;
    const onPrompt = (event: Event) => {
      event.preventDefault();
      setDeferred(event as BeforeInstallPromptEvent);
    };
    window.addEventListener("beforeinstallprompt", onPrompt);
    if (isIos()) setShowIosHelp(true);
    return () => window.removeEventListener("beforeinstallprompt", onPrompt);
  }, [dismissed]);

  const dismiss = () => {
    setDismissed(true);
    setDeferred(null);
    setShowIosHelp(false);
    try { localStorage.setItem(DISMISS_KEY, "1"); } catch { /* ignore */ }
  };

  const install = async () => {
    if (!deferred) return;
    await deferred.prompt();
    await deferred.userChoice;
    dismiss();
  };

  if (dismissed || isStandalone() || (!deferred && !showIosHelp)) return null;

  return (
    <div className="install-banner" role="status">
      {deferred ? (
        <>
          <span>Install PriceYard for quick, one-tap access to prices.</span>
          <div className="install-banner-actions">
            <button type="button" className="button button-small" onClick={() => void install()}>Install app</button>
            <button type="button" className="text-link text-link-button" onClick={dismiss}>Not now</button>
          </div>
        </>
      ) : (
        <>
          <span>Add PriceYard to your home screen: tap <strong>Share</strong>, then <strong>Add to Home Screen</strong>.</span>
          <button type="button" className="text-link text-link-button" onClick={dismiss}>Got it</button>
        </>
      )}
    </div>
  );
}
