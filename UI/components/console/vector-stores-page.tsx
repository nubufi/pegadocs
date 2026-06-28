"use client";

import { Database, Plus } from "lucide-react";
import { useState } from "react";
import { ResourceFormModal } from "@/components/console/resource-form";
import { Button } from "@/components/ui/button";
import { Card, SectionHeader } from "@/components/ui/card";
import { StatusPill } from "@/components/ui/status-pill";
import { useVectorStores } from "@/hooks/use-console-data";

export function VectorStoresPage() {
  const { stores, addStore } = useVectorStores();
  const [open, setOpen] = useState(false);

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Vector stores"
        description="Bring your own vector store. PegaDocs manages chunking, embeddings and retrieval against it."
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus size={16} />
            Connect store
          </Button>
        }
      />
      <div className="grid gap-4 min-[720px]:grid-cols-2 min-[1000px]:grid-cols-3">
        {stores.map((store) => (
          <Card key={store.id} className="p-5">
            <div className="flex items-center justify-between">
              <span className="flex h-10 w-10 items-center justify-center rounded-[10px] border border-[#dde5f3] bg-[#eef2fa] text-primary">
                <Database size={19} />
              </span>
              <StatusPill status={store.status} />
            </div>
            <div className="mt-4 font-display text-[16.5px] font-semibold text-foreground">
              {store.name}
            </div>
            <div className="mt-1 font-mono text-[12.5px] text-muted-soft">
              {store.detail}
            </div>
            <div className="mt-4 flex items-baseline gap-1.5 border-t border-[#f2f4f9] pt-4">
              <span className="font-display text-xl font-bold text-foreground">
                {store.chunks}
              </span>
              <span className="text-xs text-muted-soft">vectors indexed</span>
            </div>
          </Card>
        ))}
      </div>
      <ResourceFormModal
        open={open}
        title="Connect vector store"
        description="Create a mocked vector store connection for this frontend phase."
        fields={["name", "detail"]}
        submitLabel="Connect"
        onClose={() => setOpen(false)}
        onSubmit={(values) =>
          addStore({
            name: values.name,
            detail: values.detail ?? "new connection",
          })
        }
      />
    </div>
  );
}
