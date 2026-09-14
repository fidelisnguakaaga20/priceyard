import { createContext, useContext, useEffect, useState } from "react";

type PreferencesContextValue = {
  dataSaver: boolean;
  toggleDataSaver: () => void;
  easyReading: boolean;
  toggleEasyReading: () => void;
};

const DATA_SAVER_KEY = "priceyard_data_saver";
const EASY_READING_KEY = "priceyard_easy_reading";
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

export function PreferencesProvider({ children }: { children: React.ReactNode }) {
  const [dataSaver, setDataSaver] = useState(() => readStoredBoolean(DATA_SAVER_KEY));
  const [easyReading, setEasyReading] = useState(() => readStoredBoolean(EASY_READING_KEY));

  useEffect(() => { writeStoredBoolean(DATA_SAVER_KEY, dataSaver); }, [dataSaver]);
  useEffect(() => {
    writeStoredBoolean(EASY_READING_KEY, easyReading);
    document.documentElement.classList.toggle("easy-reading", easyReading);
  }, [easyReading]);

  const value: PreferencesContextValue = {
    dataSaver,
    toggleDataSaver: () => setDataSaver((value) => !value),
    easyReading,
    toggleEasyReading: () => setEasyReading((value) => !value),
  };

  return <PreferencesContext.Provider value={value}>{children}</PreferencesContext.Provider>;
}

export function usePreferences(): PreferencesContextValue {
  const context = useContext(PreferencesContext);
  if (!context) throw new Error("usePreferences must be used inside PreferencesProvider");
  return context;
}
