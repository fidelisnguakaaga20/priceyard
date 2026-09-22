import { createContext, useCallback, useContext, useState } from "react";
import { Toast } from "../components/Toast";
import type { ToastKind } from "../components/Toast";

export type ToastAction = { label: string; to: string };

type ToastState = {
  kind: ToastKind;
  message: string;
  action?: ToastAction;
};

type ToastContextValue = {
  showToast: (message: string, kind?: ToastKind, action?: ToastAction) => void;
};

const ToastContext = createContext<ToastContextValue | undefined>(undefined);

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toast, setToast] = useState<ToastState | null>(null);

  const dismissToast = useCallback(() => setToast(null), []);

  const showToast = useCallback((message: string, kind: ToastKind = "success", action?: ToastAction) => {
    setToast({ message, kind, action });
  }, []);

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast && <Toast kind={toast.kind} message={toast.message} action={toast.action} onDismiss={dismissToast} />}
    </ToastContext.Provider>
  );
}

export function useToast() {
  const context = useContext(ToastContext);
  if (!context) throw new Error("useToast must be used inside ToastProvider");
  return context;
}
