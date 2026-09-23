"use client";

import { login } from "@argus/api-client";
import { LoginForm } from "@argus/ui";
import { useRouter } from "next/navigation";

export default function LoginPage() {
  const router = useRouter();
  return (
    <LoginForm
      appName="Argus Operator"
      hint="Demo: op1001 / demo1234"
      onSubmit={async (username, password) => {
        const principal = await login(username, password);
        if (principal.role !== "OPERATOR") throw new Error("This account can't use this app");
        router.replace("/my-day");
      }}
    />
  );
}
