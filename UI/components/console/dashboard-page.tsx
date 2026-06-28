"use client";

import { Boxes } from "lucide-react";
import Link from "next/link";
import { Card, SectionHeader } from "@/components/ui/card";
import { StatusPill } from "@/components/ui/status-pill";
import { useDashboardData } from "@/hooks/use-console-data";

export function DashboardPage() {
  const { metrics, activity, knowledgeBases } = useDashboardData();

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Dashboard"
        description="Monitor the health of connected knowledge bases, retrieval coverage, and recent operations."
      />
      <div className="grid grid-cols-2 gap-4 min-[720px]:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.label} className="p-[18px]">
            <div className="font-mono text-[11.5px] tracking-[.02em] text-muted-soft">
              {metric.label}
            </div>
            <div className="mt-2 font-display text-3xl font-bold text-foreground">
              {metric.value}
            </div>
            <div className="mt-1 text-[12.5px] font-medium text-success">
              {metric.sub}
            </div>
          </Card>
        ))}
      </div>
      <div className="mt-4 grid gap-4 min-[820px]:grid-cols-[1.5fr_1fr]">
        <Card className="p-5">
          <div className="mb-4 flex items-center justify-between">
            <span className="font-display text-[15.5px] font-semibold text-foreground">
              Knowledge bases
            </span>
            <Link
              href="/knowledge-bases"
              className="text-[13px] font-semibold text-primary"
            >
              View all →
            </Link>
          </div>
          <div className="space-y-3">
            {knowledgeBases.map((kb) => (
              <Link
                href={`/knowledge-bases/${kb.id}`}
                key={kb.id}
                className="flex items-center gap-3 rounded-[10px] border border-[#eef1f7] px-3 py-2.5"
              >
                <span className="flex h-[34px] w-[34px] flex-none items-center justify-center rounded-[9px] bg-[#eef2fa] text-primary">
                  <Boxes size={17} />
                </span>
                <span className="min-w-0 flex-1">
                  <span className="block truncate text-sm font-semibold text-foreground">
                    {kb.name}
                  </span>
                  <span className="block truncate font-mono text-xs text-muted-soft">
                    {kb.sources} · {kb.docs} docs
                  </span>
                </span>
                <StatusPill status={kb.status} />
              </Link>
            ))}
          </div>
        </Card>
        <Card className="p-5">
          <span className="font-display text-[15.5px] font-semibold text-foreground">
            Recent activity
          </span>
          <div className="mt-3">
            {activity.map((item) => (
              <div
                key={`${item.text}-${item.time}`}
                className="flex gap-3 border-b border-[#f2f4f9] py-2.5 last:border-b-0"
              >
                <span className="mt-1.5 h-[7px] w-[7px] flex-none rounded-full bg-primary" />
                <div>
                  <div className="text-[13.5px] leading-5 text-[#33415c]">
                    {item.text}
                  </div>
                  <div className="mt-0.5 font-mono text-[11.5px] text-muted-soft">
                    {item.time}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  );
}
