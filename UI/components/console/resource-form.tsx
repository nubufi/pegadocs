"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { Plus } from "lucide-react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Field, Input, Select, Textarea } from "@/components/ui/input";
import { Modal } from "@/components/ui/modal";

const schema = z.object({
  name: z.string().min(2, "Use at least 2 characters"),
  description: z.string().optional(),
  kind: z.string().optional(),
  model: z.string().optional(),
  detail: z.string().optional(),
  type: z.string().optional(),
  scope: z.string().optional(),
});

export type ResourceFormValues = z.infer<typeof schema>;

export function ResourceFormModal({
  open,
  title,
  description,
  fields,
  submitLabel,
  onClose,
  onSubmit,
}: {
  open: boolean;
  title: string;
  description: string;
  fields: ("name" | "description" | "kind" | "model" | "detail" | "type" | "scope")[];
  submitLabel: string;
  onClose: () => void;
  onSubmit: (values: ResourceFormValues) => void;
}) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ResourceFormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      name: "",
      description: "",
      kind: "",
      model: "",
      detail: "",
      type: "SharePoint",
      scope: "",
    },
  });

  function submit(values: ResourceFormValues) {
    onSubmit(values);
    reset();
    onClose();
  }

  return (
    <Modal
      open={open}
      title={title}
      description={description}
      onClose={onClose}
    >
      <form className="space-y-4" onSubmit={handleSubmit(submit)}>
        {fields.includes("name") ? (
          <Field label="Name" error={errors.name?.message}>
            <Input placeholder="Engineering Docs" {...register("name")} />
          </Field>
        ) : null}
        {fields.includes("description") ? (
          <Field label="Description">
            <Textarea
              placeholder="What this resource is used for"
              {...register("description")}
            />
          </Field>
        ) : null}
        {fields.includes("kind") ? (
          <Field label="Kind">
            <Input placeholder="LLM + Embeddings" {...register("kind")} />
          </Field>
        ) : null}
        {fields.includes("model") ? (
          <Field label="Model">
            <Input placeholder="gpt-4o · text-embedding-3-large" {...register("model")} />
          </Field>
        ) : null}
        {fields.includes("detail") ? (
          <Field label="Connection detail">
            <Input placeholder="prod-kb · us-east-1" {...register("detail")} />
          </Field>
        ) : null}
        {fields.includes("type") ? (
          <Field label="Connector">
            <Select {...register("type")}>
              <option>SharePoint</option>
              <option>Amazon S3</option>
              <option>GitHub</option>
              <option>Confluence</option>
              <option>Notion</option>
              <option>Website</option>
            </Select>
          </Field>
        ) : null}
        {fields.includes("scope") ? (
          <Field label="Scope">
            <Input placeholder="/sites/IT-Policies" {...register("scope")} />
          </Field>
        ) : null}
        <div className="flex justify-end gap-3 pt-2">
          <Button variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit">
            <Plus size={16} />
            {submitLabel}
          </Button>
        </div>
      </form>
    </Modal>
  );
}
