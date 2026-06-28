"use client";

import { Plus, Trash2 } from "lucide-react";
import Link from "next/link";
import { useState } from "react";
import { ResourceFormModal } from "@/components/console/resource-form";
import { Button } from "@/components/ui/button";
import { SectionHeader } from "@/components/ui/card";
import { DataTable } from "@/components/ui/table";
import { StatusPill } from "@/components/ui/status-pill";
import { useCollections } from "@/hooks/use-console-data";
import type { KnowledgeBase } from "@/types/console";

export function KnowledgeBasesPage() {
  const { collections, addCollection, deleteCollection } = useCollections();
  const [open, setOpen] = useState(false);

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Knowledge bases"
        description="Each knowledge base wires together sources, a vector store and the models that answer over them."
        action={
          <Button onClick={() => setOpen(true)}>
            <Plus size={16} />
            New knowledge base
          </Button>
        }
      />
      <DataTable<KnowledgeBase>
        rows={collections}
        getKey={(row) => row.id}
        columns={[
          {
            key: "name",
            label: "Name",
            render: (row) => (
              <Link
                href={`/knowledge-bases/${row.id}`}
                className="text-sm font-semibold text-foreground hover:text-primary"
              >
                {row.name}
              </Link>
            ),
          },
          {
            key: "sources",
            label: "Sources",
            render: (row) => (
              <span className="text-[13px] text-muted">{row.sources}</span>
            ),
          },
          {
            key: "vectors",
            label: "Vector store",
            render: (row) => (
              <span className="font-mono text-[12.5px] text-primary">
                {row.vectors}
              </span>
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
            render: (row) => (
              <div className="flex items-center justify-between gap-2">
                <StatusPill status={row.status} />
                <Button
                  variant="ghost"
                  size="icon"
                  aria-label={`Delete ${row.name}`}
                  onClick={() => deleteCollection(row.id)}
                >
                  <Trash2 size={15} />
                </Button>
              </div>
            ),
          },
        ]}
      />
      <ResourceFormModal
        open={open}
        title="New knowledge base"
        description="Create a collection shell. Sources and vector stores can be attached after creation."
        fields={["name", "description"]}
        submitLabel="Create KB"
        onClose={() => setOpen(false)}
        onSubmit={(values) =>
          addCollection({
            name: values.name,
            description: values.description ?? "",
          })
        }
      />
    </div>
  );
}
