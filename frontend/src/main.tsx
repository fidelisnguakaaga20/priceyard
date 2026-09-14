import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import { PreferencesProvider } from "./context/PreferencesContext";
import { ToastProvider } from "./context/ToastContext";
import App from "./App";
import "./styles.css";
import "./mobile-nav.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <BrowserRouter>
      <ToastProvider>
        <PreferencesProvider>
          <AuthProvider>
            <App />
          </AuthProvider>
        </PreferencesProvider>
      </ToastProvider>
    </BrowserRouter>
  </React.StrictMode>,
);
