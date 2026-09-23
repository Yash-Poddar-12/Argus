"use client";

import type { ReactNode } from "react";
import { Button, LanguageSelect } from "@/components/ui";

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
