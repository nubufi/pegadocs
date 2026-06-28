"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { ResourceFormModal } from "@/components/console/resource-form";
import { Button } from "@/components/ui/button";
import { Card, SectionHeader } from "@/components/ui/card";
import { StatusPill } from "@/components/ui/status-pill";
import { useModelProviders } from "@/hooks/use-console-data";

export function ProvidersPage() {
  const { providers, addProvider } = useModelProviders();
  const [open, setOpen] = useState(false);

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Model providers"
        description="Attach any LLM and embedding provider. Keys are stored encrypted; swap models without re-indexing."
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus size={16} />
            Add provider
          </Button>
        }
      />
      <div className="grid gap-4 min-[820px]:grid-cols-2">
        {providers.map((provider) => (
          <Card key={provider.id} className="p-5">
            <div className="flex items-start justify-between gap-4">
              <div className="flex items-center gap-3">
                <span className="flex h-[42px] w-[42px] items-center justify-center rounded-[11px] border border-[#dde5f3] bg-[#eef2fa] font-mono text-sm font-semibold text-primary">
                  {provider.tag}
                </span>
                <div>
                  <div className="font-display text-base font-semibold text-foreground">
                    {provider.name}
                  </div>
                  <div className="font-mono text-[12.5px] text-muted-soft">
                    {provider.kind}
                  </div>
                </div>
              </div>
              <StatusPill status={provider.status} />
            </div>
            <div className="mt-4 rounded-[9px] border border-[#eef1f7] bg-[#f7f9fc] px-3 py-2.5 font-mono text-[12.5px] text-[#33415c]">
              {provider.model}
            </div>
          </Card>
        ))}
      </div>
      <ResourceFormModal
        open={open}
        title="Add provider"
        description="Create a mocked provider connection for the console preview."
        fields={["name", "kind", "model"]}
        submitLabel="Add provider"
        onClose={() => setOpen(false)}
        onSubmit={(values) =>
          addProvider({
            name: values.name,
            kind: values.kind ?? "LLM",
            model: values.model ?? "custom model",
          })
        }
      />
    </div>
  );
}
