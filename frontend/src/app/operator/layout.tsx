"use client";

import type { ReactNode } from "react";
import { RoleGuard } from "@/features/auth/RoleGuard";
import { OPERATOR_NAV } from "@/features/operator/nav";

export default function OperatorLayout({ children }: { children: ReactNode }) {
  return (
    <RoleGuard role="OPERATOR" appName="ARGUS Operator" nav={OPERATOR_NAV}>
      {children}
    </RoleGuard>
  );
}
