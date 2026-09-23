"use client";

// App shell (M00 built it; M02 owns it after G0): auth guard + navigation from feature manifests.
import { session, type Principal } from "@argus/api-client";
import { AppShell, I18nProvider } from "@argus/ui";
import { usePathname, useRouter } from "next/navigation";
import { useEffect, useState, type ReactNode } from "react";
import { FEATURES } from "@/features";

const REQUIRED_ROLE = "OPERATOR";

function ShellGate({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const [principal, setPrincipal] = useState<Principal | null | undefined>(undefined);

  useEffect(() => {
    setPrincipal(session.principal());
  }, [pathname]);

  const isLogin = pathname === "/login";
  const allowed = principal?.role === REQUIRED_ROLE;
  useEffect(() => {
    if (principal === undefined || isLogin) return;
    if (!allowed) router.replace("/login");
  }, [principal, allowed, isLogin, router]);

  if (isLogin) return <>{children}</>;
  if (!allowed) return null;
  return (
    <AppShell
      appName="Argus Operator"
      features={FEATURES}
      user={principal?.operator_id ?? principal?.username}
      onLogout={() => {
        session.clear();
        router.replace("/login");
      }}
    >
      {children}
    </AppShell>
  );
}

export function Providers({ children }: { children: ReactNode }) {
  return (
    <I18nProvider>
      <ShellGate>{children}</ShellGate>
    </I18nProvider>
  );
}
