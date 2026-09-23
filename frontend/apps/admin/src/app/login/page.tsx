"use client";

import { login } from "@argus/api-client";
import { LoginForm } from "@argus/ui";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  return (
    <LoginForm
      appName="Argus Supervisor"
      hint="Demo: sup001 / demo1234"
      onSubmit={async (username, password) => {
        const principal = await login(username, password);
        if (principal.role !== "SUPERVISOR_ADMIN") throw new Error("This account can't use this app");
        router.replace("/overview");
      }}
    />
  );
}
