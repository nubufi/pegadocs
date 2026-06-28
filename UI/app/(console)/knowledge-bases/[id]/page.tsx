import { KnowledgeBaseDetailPage } from "@/components/console/knowledge-base-detail-page";

export default async function Page({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  return <KnowledgeBaseDetailPage id={id} />;
}
