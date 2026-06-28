import { Suspense } from "react";
import { AuthRouteGuard } from "@/components/auth/auth-guard";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="grid min-h-screen place-items-center bg-background font-mono text-xs text-muted-soft">
          Loading session...
        </div>
      }
    >
      <AuthRouteGuard>{children}</AuthRouteGuard>
    </Suspense>
  );
}
