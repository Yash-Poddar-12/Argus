"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ButtonHTMLAttributes, ReactNode } from "react";
import { LANGUAGES, LANGUAGE_NAMES, useLanguage, type Dict, type Language } from "./i18n";

/** A feature slot's manifest (src/features/<feature>/manifest.ts). The app shell builds nav from these. */
export type FeatureManifest = {
  id: string;
  href: string;
  owner: string; // module that owns the slot, e.g. "M02" or "M07 (slot)"
  order: number;
  label: Dict<"label">;
};

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

/** Placeholder rendered by pre-registered slots until the owning module fills them. */
export function SlotPlaceholder({ title, owner, description }: { title: string; owner: string; description?: string }) {
  return (
    <div className="ui-slot">
      <h1 style={{ marginTop: 0 }}>{title}</h1>
      <p><Badge tone="info">Slot owned by {owner}</Badge></p>
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

export function LoginForm({ appName, onSubmit, hint }: {
  appName: string;
  onSubmit: (username: string, password: string) => Promise<void>;
  hint?: ReactNode;
}) {
  return (
    <div className="ui-center">
      <form
        className="ui-card ui-stack"
        style={{ width: "min(420px, 100%)" }}
        onSubmit={async (e) => {
          e.preventDefault();
          const form = e.currentTarget;
          const data = new FormData(form);
          const out = form.querySelector("[data-error]") as HTMLElement;
          out.textContent = "";
          try {
            await onSubmit(String(data.get("username")), String(data.get("password")));
          } catch (err) {
            out.textContent = err instanceof Error ? err.message : "Login failed";
          }
        }}
      >
        <div className="ui-brand" style={{ padding: 0 }}><span className="ui-brand-mark" aria-hidden />{appName}</div>
        <label className="ui-stack" style={{ gap: 4 }}>Username<input className="ui-input" name="username" autoComplete="username" required /></label>
        <label className="ui-stack" style={{ gap: 4 }}>Password<input className="ui-input" name="password" type="password" autoComplete="current-password" required /></label>
        <Button variant="primary" type="submit">Sign in</Button>
        <div data-error role="alert" style={{ color: "var(--danger)", fontWeight: 600 }} />
        {hint && <div className="ui-muted" style={{ fontSize: "0.9rem" }}>{hint}</div>}
        <LanguageSelect />
      </form>
    </div>
  );
}

export function AppShell({ appName, features, user, onLogout, banner, children }: {
  appName: string;
  features: FeatureManifest[];
  user?: string;
  onLogout?: () => void;
  banner?: ReactNode;
  children: ReactNode;
}) {
  const pathname = usePathname();
  const { lang } = useLanguage();
  const items = [...features].sort((a, b) => a.order - b.order);
  return (
    <div className="ui-shell">
      <nav className="ui-nav" aria-label="Main">
        <div className="ui-brand"><span className="ui-brand-mark" aria-hidden />{appName}</div>
        {items.map((f) => (
          <Link key={f.id} href={f.href} aria-current={pathname?.startsWith(f.href) ? "page" : undefined}>
            {f.label[lang]?.label ?? f.label.en.label}
          </Link>
        ))}
        <div className="ui-nav-footer">
          <LanguageSelect />
          {user && <span>{user}</span>}
          {onLogout && <Button onClick={onLogout}>Log out</Button>}
        </div>
      </nav>
      <main className="ui-main">
        {banner}
        {children}
      </main>
    </div>
  );
}
