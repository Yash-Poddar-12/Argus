"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";
import { Button, LanguageSelect } from "@/components/ui";
import { useLanguage, type Dict } from "@/lib/i18n";

export type NavItem = { href: string; label: Dict<"label"> };

export function AppShell({ appName, nav, user, onLogout, banner, children }: {
  appName: string;
  nav: NavItem[];
  user?: string;
  onLogout?: () => void;
  banner?: ReactNode;
  children: ReactNode;
}) {
  const pathname = usePathname();
  const { lang } = useLanguage();
  return (
    <div className="ui-shell">
      <nav className="ui-nav" aria-label="Main">
        <div className="ui-brand"><span className="ui-brand-mark" aria-hidden />{appName}</div>
        {nav.map((item) => (
          <Link key={item.href} href={item.href} aria-current={pathname?.startsWith(item.href) ? "page" : undefined}>
            {item.label[lang]?.label ?? item.label.en.label}
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
