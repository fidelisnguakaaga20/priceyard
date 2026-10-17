import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { PreferencesProvider } from "./context/PreferencesContext";
import { ToastProvider } from "./context/ToastContext";
import { ErrorBoundary } from "./components/ErrorBoundary";
import App from "./App";
import { getApiBase } from "./services/api";
import "./styles.css";
import "./mobile-nav.css";

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    try {
      const worker = new URL("/sw.js", window.location.origin);
      const api = new URL(getApiBase(), window.location.origin);
      if (api.username || api.password || api.search || api.hash) return;
      worker.searchParams.set("api", api.href);
      navigator.serviceWorker.register(worker.href).catch(() => {});
    } catch { /* Offline support is optional when configuration is invalid. */ }
  });
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ErrorBoundary>
        <ToastProvider>
          <PreferencesProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </PreferencesProvider>
        </ToastProvider>
      </ErrorBoundary>
    </BrowserRouter>
  </React.StrictMode>,
);
