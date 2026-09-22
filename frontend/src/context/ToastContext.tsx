import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
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
  const timeoutRef = useRef<number | null>(null);

  const dismissToast = useCallback(() => {
    if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    timeoutRef.current = null;
    setToast(null);
  }, []);

  const showToast = useCallback((message: string, kind: ToastKind = "success", action?: ToastAction) => {
    if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
    setToast({ message, kind, action });
    timeoutRef.current = window.setTimeout(() => {
      setToast(null);
      timeoutRef.current = null;
    }, 4500);
  }, []);

  useEffect(() => () => {
    if (timeoutRef.current !== null) window.clearTimeout(timeoutRef.current);
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
