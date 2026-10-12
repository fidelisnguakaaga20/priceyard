import { createContext, useContext, useEffect, useState } from "react";

type PreferencesContextValue = {
  dataSaver: boolean;
  toggleDataSaver: () => void;
  easyReading: boolean;
  toggleEasyReading: () => void;
  darkMode: boolean;
  toggleDarkMode: () => void;
};

const DATA_SAVER_KEY = "priceyard_data_saver";
const EASY_READING_KEY = "priceyard_easy_reading";
const DARK_MODE_KEY = "priceyard_dark_mode";
const PreferencesContext = createContext<PreferencesContextValue | undefined>(undefined);

function readStoredBoolean(key: string): boolean {
  try {
    return localStorage.getItem(key) === "1";
  } catch {
    return false;
  }
}

function writeStoredBoolean(key: string, value: boolean) {
  try {
    localStorage.setItem(key, value ? "1" : "0");
  } catch {
    // ignore storage failures (private browsing, blocked storage, etc.)
  }
}

/** null = no explicit choice yet -- follow the device's own dark/light setting
 * (handled purely in CSS via prefers-color-scheme). Once toggled, the explicit
 * choice always wins, same as every other site's dark mode switch. */
function readStoredTheme(): boolean | null {
  try {
    const value = localStorage.getItem(DARK_MODE_KEY);
    if (value === "1") return true;
    if (value === "0") return false;
    return null;
  } catch {
    return null;
  }
}

function systemPrefersDark(): boolean {
  try {
    return window.matchMedia("(prefers-color-scheme: dark)").matches;
  } catch {
    return false;
  }
}

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const [dataSaver, setDataSaver] = useState(() => readStoredBoolean(DATA_SAVER_KEY));
  const [easyReading, setEasyReading] = useState(() => readStoredBoolean(EASY_READING_KEY));
  const [darkOverride, setDarkOverride] = useState<boolean | null>(() => readStoredTheme());
  const darkMode = darkOverride ?? systemPrefersDark();

  useEffect(() => { writeStoredBoolean(DATA_SAVER_KEY, dataSaver); }, [dataSaver]);
  useEffect(() => {
    writeStoredBoolean(EASY_READING_KEY, easyReading);
    document.documentElement.classList.toggle("easy-reading", easyReading);
  }, [easyReading]);
  useEffect(() => {
    if (darkOverride === null) {
      document.documentElement.removeAttribute("data-theme");
    } else {
      document.documentElement.setAttribute("data-theme", darkOverride ? "dark" : "light");
    }
  }, [darkOverride]);

  const value: PreferencesContextValue = {
    dataSaver,
    toggleDataSaver: () => setDataSaver((value) => !value),
    easyReading,
    toggleEasyReading: () => setEasyReading((value) => !value),
    darkMode,
    toggleDarkMode: () => {
      const next = !darkMode;
      writeStoredBoolean(DARK_MODE_KEY, next);
      setDarkOverride(next);
    },
  };

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences(): PreferencesContextValue {
  const context = useContext(PreferencesContext);
  if (!context) throw new Error("usePreferences must be used inside PreferencesProvider");
  return context;
}
