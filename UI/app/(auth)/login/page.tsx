import { Suspense } from "react";
import { LoginRegisterForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export default function LoginPage() {
  return (
    <AuthShell mode="login">
      <Suspense fallback={null}>
        <LoginRegisterForm mode="login" />
      </Suspense>
    </AuthShell>
  );
}
