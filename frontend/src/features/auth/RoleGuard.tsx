"use client";

// Guards an area (/operator or /supervisor) by role and renders the app shell with that area's navigation.
// The backend enforces permissions and site scope; this guard only routes users to the right area.
import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";
import { AppShell, type NavItem } from "@/components/layout/AppShell";
import { useSession } from "@/hooks/useSession";
import { session, type Principal } from "@/lib/api";

export const HOME_BY_ROLE: Record<Principal["role"], string> = {
  OPERATOR: "/operator/my-day",
  SUPERVISOR_ADMIN: "/supervisor/overview",
};

export function RoleGuard({ role, appName, nav, children }: {
  role: Principal["role"];
  appName: string;
  nav: NavItem[];
  children: ReactNode;
}) {
  const router = useRouter();
  const principal = useSession();

  useEffect(() => {
    if (principal === undefined) return;
    if (principal === null) router.replace("/login");
    else if (principal.role !== role) router.replace(HOME_BY_ROLE[principal.role]);
  }, [principal, role, router]);

  if (!principal || principal.role !== role) return null;
  return (
    <AppShell
      appName={appName}
      nav={nav}
      user={principal.operator_id ?? principal.username}
      onLogout={() => {
        session.clear();
        router.replace("/login");
      }}
    >
      {children}
    </AppShell>
  );
}
