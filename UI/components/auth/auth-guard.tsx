"use client";

import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useEffect } from "react";
import { useAuthStore } from "@/stores/auth";

export function ConsoleAuthGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();
  const { hydrated, accessToken, refreshToken, expiresAt, refreshSession } =
    useAuthStore();

  useEffect(() => {
    if (!hydrated) return;

    async function ensureSession() {
      if (!accessToken) {
        const next = `${pathname}${
          searchParams.toString() ? `?${searchParams.toString()}` : ""
        }`;
        router.replace(`/login?next=${encodeURIComponent(next)}`);
        return;
      }

      if (refreshToken && expiresAt && expiresAt - Date.now() < 60_000) {
        const refreshed = await refreshSession();
        if (!refreshed) {
          router.replace(`/login?next=${encodeURIComponent(pathname)}`);
        }
      }
    }

    void ensureSession();
  }, [
    accessToken,
    expiresAt,
    hydrated,
    pathname,
    refreshSession,
    refreshToken,
    router,
    searchParams,
  ]);

  if (!hydrated) {
    return (
      <div className="grid min-h-screen place-items-center bg-console font-mono text-xs text-muted-soft">
        Loading session...
      </div>
    );
  }

  if (!accessToken) return null;

  return children;
}

export function AuthRouteGuard({ children }: { children: React.ReactNode }) {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { hydrated, accessToken } = useAuthStore();

  useEffect(() => {
    if (!hydrated || !accessToken) return;
    router.replace(searchParams.get("next") || "/dashboard");
  }, [accessToken, hydrated, router, searchParams]);

  if (!hydrated) {
    return (
      <div className="grid min-h-screen place-items-center bg-background font-mono text-xs text-muted-soft">
        Loading session...
      </div>
    );
  }

  if (accessToken) return null;

  return children;
}
