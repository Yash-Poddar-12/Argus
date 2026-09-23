"use client";

import { createContext, useCallback, useContext, useMemo, useSyncExternalStore, type ReactNode } from "react";

/** UI languages (docs: en, hi, ta initially). Language is an interaction layer only. */
export const LANGUAGES = ["en", "hi", "ta"] as const;
export type Language = (typeof LANGUAGES)[number];
export const LANGUAGE_NAMES: Record<Language, string> = { en: "English", hi: "हिन्दी", ta: "தமிழ்" };

/** Each feature owns its strings: `const dict = { en: {...}, hi: {...}, ta: {...} }` (no shared string file). */
export type Dict<K extends string = string> = { en: Record<K, string> } & Partial<Record<Language, Partial<Record<K, string>>>>;

type Ctx = { lang: Language; setLang: (l: Language) => void };
const LanguageContext = createContext<Ctx>({ lang: "en", setLang: () => {} });
const STORAGE_KEY = "argus.lang";

const LANG_EVENT = "argus:lang";

function subscribe(onChange: () => void) {
  window.addEventListener(LANG_EVENT, onChange);
  window.addEventListener("storage", onChange);
  return () => {
    window.removeEventListener(LANG_EVENT, onChange);
    window.removeEventListener("storage", onChange);
  };
}

function readLang(): Language {
  try {
    const saved = localStorage.getItem(STORAGE_KEY) as Language | null;
    return saved && LANGUAGES.includes(saved) ? saved : "en";
  } catch {
    return "en";
  }
}

export function I18nProvider({ children }: { children: ReactNode }) {
  const lang = useSyncExternalStore(subscribe, readLang, () => "en" as Language);
  const setLang = useCallback((l: Language) => {
    try { localStorage.setItem(STORAGE_KEY, l); } catch {}
    document.documentElement.lang = l;
    window.dispatchEvent(new Event(LANG_EVENT));
  }, []);
  const value = useMemo(() => ({ lang, setLang }), [lang, setLang]);
  return <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>;
}

export function useLanguage() {
  return useContext(LanguageContext);
}

/** `const t = useT(dict); t("title")`. Falls back to English, then the key. */
export function useT<K extends string>(dict: Dict<K>) {
  const { lang } = useLanguage();
  return useCallback((key: K) => dict[lang]?.[key] ?? dict.en[key] ?? key, [dict, lang]);
}
