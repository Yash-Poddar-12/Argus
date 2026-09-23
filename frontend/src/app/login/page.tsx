"use client";

import { useRouter } from "next/navigation";
import { LoginForm } from "@/features/auth/LoginForm";
import { HOME_BY_ROLE } from "@/features/auth/RoleGuard";
import { login } from "@/lib/api";

export default function LoginPage() {
  const router = useRouter();
  return (
    <LoginForm
      appName="ARGUS"
      hint="Demo: op1001 (operator) or sup001 (supervisor), password demo1234"
      onSubmit={async (username, password) => {
        const principal = await login(username, password);
        router.replace(HOME_BY_ROLE[principal.role]);
      }}
    />
  );
}
