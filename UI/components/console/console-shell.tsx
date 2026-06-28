"use client";

import {
  Bot,
  Boxes,
  Database,
  Home,
  Menu,
  MessageSquareText,
  Search,
  ServerCog,
  Share2,
} from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import { Avatar } from "@/components/ui/avatar";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

const sections = [
  {
    label: "WORKSPACE",
    items: [
      { href: "/dashboard", label: "Dashboard", icon: Home },
      { href: "/knowledge-bases", label: "Knowledge bases", icon: Boxes },
    ],
  },
  {
    label: "CONNECTIONS",
    items: [
      { href: "/model-providers", label: "Model providers", icon: ServerCog },
      { href: "/vector-stores", label: "Vector stores", icon: Database },
      { href: "/data-sources", label: "Data sources", icon: Share2 },
    ],
  },
  {
    label: "TALK TO IT",
    items: [
      { href: "/chat", label: "Chat playground", icon: MessageSquareText },
      { href: "/channels", label: "Channels & bots", icon: Bot },
    ],
  },
];

const titles: Record<string, string> = {
  "/dashboard": "Dashboard",
  "/knowledge-bases": "Knowledge bases",
  "/model-providers": "Model providers",
  "/vector-stores": "Vector stores",
  "/data-sources": "Data sources",
  "/chat": "Chat playground",
  "/channels": "Channels & bots",
  "/account": "Account",
};

function titleFor(pathname: string) {
  if (pathname.startsWith("/knowledge-bases/")) return "Knowledge base";
  return titles[pathname] ?? "Dashboard";
}

function Sidebar({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <aside className="flex h-full w-[248px] flex-none flex-col bg-navy px-3.5 py-[18px]">
      <Link href="/dashboard" className="mb-5 flex items-center gap-2.5 px-2">
        <Image
          src="/pegadocs-mark-white.png"
          alt="PegaDocs"
          width={28}
          height={28}
          className="rounded-md"
          priority
        />
        <span className="font-display text-lg font-bold text-white">
          PegaDocs
        </span>
      </Link>

      <nav className="flex-1">
        {sections.map((section) => (
          <div key={section.label}>
            <div className="px-2.5 pb-1.5 pt-4 font-mono text-[10.5px] tracking-[.08em] text-[#566688] first:pt-0">
              {section.label}
            </div>
            {section.items.map((item) => {
              const Icon = item.icon;
              const active =
                pathname === item.href ||
                (item.href === "/knowledge-bases" &&
                  pathname.startsWith("/knowledge-bases/"));
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onNavigate}
                  className={cn(
                    "mb-0.5 flex items-center gap-3 rounded-[9px] px-3 py-2.5 text-sm font-medium transition-colors",
                    active
                      ? "bg-white/10 text-white"
                      : "text-[#9aa6bd] hover:bg-white/5 hover:text-white",
                  )}
                >
                  <Icon size={17} strokeWidth={1.9} />
                  {item.label}
                </Link>
              );
            })}
          </div>
        ))}
      </nav>

      <div className="rounded-[13px] border border-white/10 bg-white/[.06] p-3">
        <div className="flex items-center gap-2">
          <span className="h-[7px] w-[7px] rounded-full bg-[#3ad08a]" />
          <span className="font-mono text-[11px] text-[#aebbd6]">
            prod · self-hosted
          </span>
        </div>
        <div className="mt-2 text-xs leading-5 text-[#7b8aab]">
          4 KBs · 4 providers · 5 sources synced
        </div>
      </div>
    </aside>
  );
}

export function ConsoleShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="flex h-screen min-h-[680px] overflow-hidden bg-console text-muted">
      <div className="hidden md:block">
        <Sidebar />
      </div>

      {mobileOpen ? (
        <div className="fixed inset-0 z-40 md:hidden">
          <button
            type="button"
            aria-label="Close sidebar"
            className="absolute inset-0 bg-navy/45"
            onClick={() => setMobileOpen(false)}
          />
          <div className="relative h-full">
            <Sidebar onNavigate={() => setMobileOpen(false)} />
          </div>
        </div>
      ) : null}

      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex h-[60px] flex-none items-center gap-4 border-b border-border bg-white px-4 md:px-6">
          <Button
            variant="ghost"
            size="icon"
            className="md:hidden"
            aria-label="Open sidebar"
            onClick={() => setMobileOpen(true)}
          >
            <Menu size={19} />
          </Button>
          <div className="font-display text-base font-semibold text-foreground">
            {titleFor(pathname)}
          </div>
          <div className="ml-auto hidden w-[280px] items-center gap-2.5 rounded-[9px] border border-border bg-console px-3 py-2 min-[1100px]:flex">
            <Search size={15} className="text-muted-soft" />
            <span className="text-[13.5px] text-muted-soft">
              Search knowledge bases...
            </span>
          </div>
          <div className="flex items-center gap-2 rounded-lg border border-[#dde5f3] bg-[#eef2fa] px-3 py-1.5 font-mono text-xs font-semibold text-primary">
            <span className="h-1.5 w-1.5 rounded-full bg-primary" />
            production
          </div>
          <Link href="/account" aria-label="Account">
            <Avatar initials="NB" size="sm" />
          </Link>
        </header>
        <div data-scroll className="flex-1 overflow-y-auto p-4 md:p-7">
          {children}
        </div>
      </main>
    </div>
  );
}
