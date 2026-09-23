"use client";

import { useRouter } from "next/navigation";
import { useEffect } from "react";
import { HOME_BY_ROLE } from "@/features/auth/RoleGuard";
import { session } from "@/lib/api";

export default function Home() {
  const router = useRouter();
  useEffect(() => {
    const principal = session.principal();
    router.replace(principal ? HOME_BY_ROLE[principal.role] : "/login");
  }, [router]);
  return null;
}
