import { Suspense } from "react";
import { ConsoleAuthGuard } from "@/components/auth/auth-guard";
import { ConsoleShell } from "@/components/console/console-shell";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <Suspense
      fallback={
        <div className="grid min-h-screen place-items-center bg-console font-mono text-xs text-muted-soft">
          Loading session...
        </div>
      }
    >
      <ConsoleAuthGuard>
        <ConsoleShell>{children}</ConsoleShell>
      </ConsoleAuthGuard>
    </Suspense>
  );
}
