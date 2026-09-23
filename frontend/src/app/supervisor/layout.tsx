"use client";

import type { ReactNode } from "react";
import { RoleGuard } from "@/features/auth/RoleGuard";
import { SUPERVISOR_NAV } from "@/features/supervisor/nav";

export default function SupervisorLayout({ children }: { children: ReactNode }) {
  return (
    <RoleGuard role="SUPERVISOR_ADMIN" appName="ARGUS Supervisor" nav={SUPERVISOR_NAV}>
      {children}
    </RoleGuard>
  );
}
