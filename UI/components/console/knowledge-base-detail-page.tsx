"use client";

import { Play, Plus, RefreshCw } from "lucide-react";
import { useState } from "react";
import { ResourceFormModal } from "@/components/console/resource-form";
import { Button } from "@/components/ui/button";
import { Card, SectionHeader } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { StatusPill } from "@/components/ui/status-pill";
import { useCollection, useDataSources } from "@/hooks/use-console-data";
import type { DataSource } from "@/types/console";

export function KnowledgeBaseDetailPage({ id }: { id: string }) {
  const { collection } = useCollection(id);
  const { sources, addSource } = useDataSources(collection.id);
  const [open, setOpen] = useState(false);

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title={collection.name}
        description={collection.description}
        action={
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary">
              <RefreshCw size={16} />
              Scan
            </Button>
            <Button>
              <Play size={16} />
              Embed
            </Button>
          </div>
        }
      />
      <div className="mb-4 grid gap-4 min-[720px]:grid-cols-3">
        <Card className="p-5">
          <div className="font-mono text-[11.5px] text-muted-soft">Sources</div>
          <div className="mt-2 font-display text-2xl font-bold text-foreground">
            {sources.length}
          </div>
        </Card>
        <Card className="p-5">
          <div className="font-mono text-[11.5px] text-muted-soft">Documents</div>
          <div className="mt-2 font-display text-2xl font-bold text-foreground">
            {collection.docs}
          </div>
        </Card>
        <Card className="p-5">
          <div className="font-mono text-[11.5px] text-muted-soft">Status</div>
          <div className="mt-3">
            <StatusPill status={collection.status} />
          </div>
        </Card>
      </div>
      <div className="mb-4 flex items-center justify-between">
        <h2 className="font-display text-lg font-semibold text-foreground">
          Data sources
        </h2>
        <Button variant="secondary" onClick={() => setOpen(true)}>
          <Plus size={16} />
          Add source
        </Button>
      </div>
      <DataTable<DataSource>
        rows={sources}
        getKey={(row) => row.id}
        columns={[
          {
            key: "name",
            label: "Source",
            render: (row) => (
              <span className="text-sm font-semibold text-foreground">
                {row.name}
              </span>
            ),
          },
          {
            key: "type",
            label: "Connector",
            render: (row) => <span className="text-[13px] text-muted">{row.type}</span>,
          },
          {
            key: "scope",
            label: "Scope",
            render: (row) => (
              <span className="font-mono text-xs text-primary">{row.scope}</span>
            ),
          },
          {
            key: "docs",
            label: "Docs",
            render: (row) => (
              <span className="font-mono text-[13px] text-[#33415c]">
                {row.docs}
              </span>
            ),
          },
          {
            key: "status",
            label: "Status",
            render: (row) => <StatusPill status={row.status} />,
          },
        ]}
      />
      <ResourceFormModal
        open={open}
        title="Add data source"
        description="Attach a source to this knowledge base. Credentials are mocked in this phase."
        fields={["name", "type", "scope"]}
        submitLabel="Add source"
        onClose={() => setOpen(false)}
        onSubmit={(values) =>
          addSource({
            name: values.name,
            type: values.type ?? "SharePoint",
            scope: values.scope ?? "",
            collectionId: collection.id,
          })
        }
      />
    </div>
  );
}
