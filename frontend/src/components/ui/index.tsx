"use client";

// Shared UI primitives (design tokens in src/app/globals.css). Product-specific components belong in src/features/<feature>/.
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { LANGUAGES, LANGUAGE_NAMES, useLanguage, type Language } from "@/lib/i18n";

export function Button({ variant = "default", ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: "default" | "primary" | "danger" }) {
  return <button {...props} className={`ui-btn ${variant === "default" ? "" : variant} ${props.className ?? ""}`} />;
}

export function Card({ title, children, actions }: { title?: ReactNode; children?: ReactNode; actions?: ReactNode }) {
  return (
    <section className="ui-card">
      {(title || actions) && (
        <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
          <h2 style={{ margin: 0, fontSize: "1.1rem" }}>{title}</h2>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

export type Tone = "ok" | "warn" | "danger" | "info" | "neutral";
export function Badge({ tone = "neutral", children }: { tone?: Tone; children: ReactNode }) {
  return <span className={`ui-badge ${tone === "neutral" ? "" : tone}`}>{children}</span>;
}

export function Stat({ label, value, hint }: { label: ReactNode; value: ReactNode; hint?: ReactNode }) {
  return (
    <div className="ui-card">
      <div className="ui-stat-label">{label}</div>
      <div className="ui-stat-value">{value}</div>
      {hint && <div className="ui-muted">{hint}</div>}
    </div>
  );
}

/** Placeholder rendered by a page until its feature is built. */
export function SlotPlaceholder({ title, owner, description }: { title: string; owner: string; description?: string }) {
  return (
    <div className="ui-slot">
      <h1 style={{ marginTop: 0 }}>{title}</h1>
      <p><Badge tone="info">Placeholder · {owner}</Badge></p>
      {description && <p className="ui-muted">{description}</p>}
    </div>
  );
}

export function LanguageSelect() {
  const { lang, setLang } = useLanguage();
  return (
    <select aria-label="Language" className="ui-input" value={lang} onChange={(e) => setLang(e.target.value as Language)}>
      {LANGUAGES.map((l) => <option key={l} value={l}>{LANGUAGE_NAMES[l]}</option>)}
    </select>
  );
}
