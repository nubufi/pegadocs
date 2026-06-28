import { Suspense } from "react";
import { LoginRegisterForm } from "@/components/auth/auth-form";
import { AuthShell } from "@/components/auth/auth-shell";

export default function RegisterPage() {
  return (
    <AuthShell mode="register">
      <Suspense fallback={null}>
        <LoginRegisterForm mode="register" />
      </Suspense>
    </AuthShell>
  );
}
