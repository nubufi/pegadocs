"use client";

import { Plus } from "lucide-react";
import { useState } from "react";
import { ResourceFormModal } from "@/components/console/resource-form";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { StatusPill } from "@/components/ui/status-pill";
import { useDataSources } from "@/hooks/use-console-data";
import type { DataSource } from "@/types/console";

export function DataSourcesPage() {
  const { sources, addSource } = useDataSources();
  const [open, setOpen] = useState(false);

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Data sources"
        description="Connect SharePoint, S3, Confluence and more. Scheduled syncs keep the index fresh automatically."
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus size={16} />
            Add source
          </Button>
        }
      />
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
            label: "Sync",
            render: (row) => <StatusPill status={row.status} />,
          },
        ]}
      />
      <ResourceFormModal
        open={open}
        title="Add source"
        description="Attach a mocked connector. Dynamic credential forms come with backend wiring."
        fields={["name", "type", "scope"]}
        submitLabel="Add source"
        onClose={() => setOpen(false)}
        onSubmit={(values) =>
          addSource({
            name: values.name,
            type: values.type ?? "SharePoint",
            scope: values.scope ?? "",
          })
        }
      />
    </div>
  );
}
