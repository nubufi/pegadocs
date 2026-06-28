"use client";

import { Monitor, Plus, Smartphone } from "lucide-react";
import { useRouter } from "next/navigation";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Field, Input } from "@/components/ui/input";
import { StatusPill } from "@/components/ui/status-pill";
import { useAccountData } from "@/hooks/use-console-data";
import { getInitials, useAuthStore } from "@/stores/auth";

export function AccountPage() {
  const router = useRouter();
  const user = useAuthStore((state) => state.user);
  const clearSession = useAuthStore((state) => state.clearSession);
  const { profile, apiKeys, sessions } = useAccountData();
  const displayName = user?.name || profile.name;
  const displayEmail = user?.email || profile.email;

  function logout() {
    clearSession();
    router.replace("/login");
  }

  return (
    <div className="mx-auto max-w-[860px]">
      <Card className="flex flex-wrap items-center gap-5 p-6">
        <Avatar initials={getInitials(user) || profile.initials} size="lg" />
        <div className="min-w-0 flex-1">
          <div className="flex flex-wrap items-center gap-2">
            <span className="font-display text-[21px] font-bold text-foreground">
              {displayName}
            </span>
            <span className="rounded-md border border-[#dde5f3] bg-[#eef2fa] px-2.5 py-1 font-mono text-[11px] font-semibold text-primary">
              OWNER
            </span>
          </div>
          <div className="mt-1 text-sm text-idle">
            {displayEmail} · joined Jan 2026
          </div>
        </div>
        <Button variant="danger" onClick={logout}>
          Sign out
        </Button>
      </Card>

      <Card className="mt-4 p-6">
        <div className="font-display text-base font-semibold text-foreground">
          Profile details
        </div>
        <div className="mt-5 grid gap-4 min-[720px]:grid-cols-2">
          <Field label="Full name">
            <Input defaultValue={displayName} />
          </Field>
          <Field label="Email">
            <Input defaultValue={displayEmail} type="email" />
          </Field>
          <Field label="Workspace">
            <Input defaultValue={profile.workspace} />
          </Field>
          <Field label="Timezone">
            <Input defaultValue={profile.timezone} />
          </Field>
        </div>
        <div className="mt-5 flex gap-3">
          <Button>Save changes</Button>
          <Button variant="secondary">Cancel</Button>
        </div>
      </Card>

      <Card className="mt-4 p-6">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <div className="font-display text-base font-semibold text-foreground">
              API keys
            </div>
            <div className="mt-0.5 text-[13px] text-muted-soft">
              Authenticate against the PegaDocs REST API.
            </div>
          </div>
          <Button variant="secondary">
            <Plus size={15} />
            New key
          </Button>
        </div>
        <div className="mt-4 space-y-3">
          {apiKeys.map((key) => (
            <div
              key={key.id}
              className="flex flex-wrap items-center gap-3 rounded-[10px] border border-[#eef1f7] px-4 py-3"
            >
              <span className="text-sm font-semibold text-foreground">{key.name}</span>
              <span className="rounded-lg border border-[#eef1f7] bg-[#f7f9fc] px-2.5 py-1 font-mono text-[12.5px] text-muted">
                {key.value}
              </span>
              <span className="ml-auto font-mono text-[11.5px] text-muted-soft">
                {key.lastUsed}
              </span>
              <button className="text-[13px] font-semibold text-primary">Copy</button>
              <button className="text-[13px] font-semibold text-error">Revoke</button>
            </div>
          ))}
        </div>
      </Card>

      <Card className="mt-4 p-6">
        <div className="font-display text-base font-semibold text-foreground">
          Active sessions
        </div>
        <div className="mt-4 space-y-3">
          {sessions.map((session) => {
            const Icon = session.current ? Monitor : Smartphone;
            return (
              <div
                key={session.id}
                className="flex items-center gap-3 rounded-[10px] border border-[#eef1f7] px-4 py-3"
              >
                <span className="flex h-9 w-9 flex-none items-center justify-center rounded-[9px] bg-[#eef2fa] text-primary">
                  <Icon size={18} />
                </span>
                <div className="min-w-0 flex-1">
                  <div className="text-sm font-semibold text-foreground">
                    {session.device}
                  </div>
                  <div className="font-mono text-xs text-muted-soft">
                    {session.detail}
                  </div>
                </div>
                {session.current ? (
                  <StatusPill status="active" label="Current" />
                ) : (
                  <button className="text-[13px] font-semibold text-error">
                    Revoke
                  </button>
                )}
              </div>
            );
          })}
        </div>
      </Card>
    </div>
  );
}
