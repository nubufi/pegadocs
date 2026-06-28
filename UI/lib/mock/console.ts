import type {
  ActivityItem,
  ApiKey,
  Channel,
  ChatMessage,
  ChatSuggestion,
  DataSource,
  KnowledgeBase,
  Metric,
  ModelProvider,
  Session,
  VectorStore,
} from "@/types/console";

export const metrics: Metric[] = [
  { label: "Knowledge bases", value: "4", sub: "all healthy" },
  { label: "Documents indexed", value: "18,420", sub: "+820 this week" },
  { label: "Queries · 7d", value: "2,310", sub: "+12% vs prev" },
  { label: "Avg response", value: "840ms", sub: "p50 latency" },
];

export const activity: ActivityItem[] = [
  { text: "Engineering Docs sync started", time: "just now" },
  { text: "Azure OpenAI key rotated", time: "1h ago" },
  { text: "210 documents added to Company Wiki", time: "3h ago" },
  { text: "Telegram bot answered 48 queries", time: "today" },
  { text: "pgvector reindex completed", time: "yesterday" },
];

export const knowledgeBases: KnowledgeBase[] = [
  {
    id: "company-wiki",
    name: "Company Wiki",
    sources: "SharePoint, Confluence",
    vectors: "pinecone",
    docs: "8,240",
    status: "active",
    description: "Company-wide operating knowledge and policy answers.",
  },
  {
    id: "hr-policies",
    name: "HR & Policies",
    sources: "Amazon S3, Drive",
    vectors: "pgvector",
    docs: "3,110",
    status: "active",
    description: "Employee handbook, leave policies, and payroll guidance.",
  },
  {
    id: "engineering-docs",
    name: "Engineering Docs",
    sources: "GitHub, Notion",
    vectors: "qdrant",
    docs: "5,870",
    status: "syncing",
    description: "Architecture decisions, runbooks, and platform docs.",
  },
  {
    id: "support-kb",
    name: "Support KB",
    sources: "Zendesk, Web",
    vectors: "pinecone",
    docs: "1,200",
    status: "idle",
    description: "Troubleshooting articles and customer-facing FAQs.",
  },
];

export const modelProviders: ModelProvider[] = [
  {
    id: "azure-openai",
    name: "Azure OpenAI",
    tag: "AZ",
    kind: "LLM + Embeddings",
    model: "gpt-4o · text-embedding-3-large",
    status: "active",
  },
  {
    id: "aws-bedrock",
    name: "AWS Bedrock",
    tag: "BR",
    kind: "LLM",
    model: "anthropic.claude-3-5-sonnet",
    status: "active",
  },
  {
    id: "openrouter",
    name: "OpenRouter",
    tag: "OR",
    kind: "LLM router",
    model: "auto · 40+ models available",
    status: "active",
  },
  {
    id: "ollama",
    name: "Ollama",
    tag: "OL",
    kind: "LLM · local",
    model: "llama3.1:70b",
    status: "idle",
  },
];

export const vectorStores: VectorStore[] = [
  {
    id: "pinecone",
    name: "Pinecone",
    detail: "prod-kb · us-east-1",
    chunks: "1.24M",
    status: "active",
  },
  {
    id: "pgvector",
    name: "pgvector",
    detail: "pg-main · hr schema",
    chunks: "310K",
    status: "active",
  },
  {
    id: "qdrant",
    name: "Qdrant",
    detail: "eng-cluster",
    chunks: "587K",
    status: "syncing",
  },
];

export const dataSources: DataSource[] = [
  {
    id: "it-sharepoint",
    collectionId: "company-wiki",
    name: "IT SharePoint",
    type: "SharePoint",
    scope: "/sites/IT-Policies",
    docs: "2,140",
    status: "active",
  },
  {
    id: "hr-docs-bucket",
    collectionId: "hr-policies",
    name: "HR Docs Bucket",
    type: "Amazon S3",
    scope: "s3://hr-docs",
    docs: "1,860",
    status: "active",
  },
  {
    id: "eng-handbook",
    collectionId: "engineering-docs",
    name: "Eng Handbook",
    type: "GitHub",
    scope: "org/handbook",
    docs: "920",
    status: "active",
  },
  {
    id: "confluence-space",
    collectionId: "company-wiki",
    name: "Confluence Space",
    type: "Confluence",
    scope: "PLATFORM",
    docs: "3,400",
    status: "syncing",
  },
  {
    id: "product-notion",
    collectionId: "engineering-docs",
    name: "Product Notion",
    type: "Notion",
    scope: "Product wiki",
    docs: "1,120",
    status: "error",
  },
];

export const channels: Channel[] = [
  {
    id: "web-widget",
    name: "Web widget",
    desc: "Embeddable chat bubble",
    meta: "embed snippet",
    status: "live",
  },
  {
    id: "teams",
    name: "Microsoft Teams",
    desc: "Bot in your tenant",
    meta: "azure bot · app id",
    status: "live",
  },
  {
    id: "telegram",
    name: "Telegram",
    desc: "@PegaDocsBot",
    meta: "bot token",
    status: "live",
  },
  {
    id: "rest-api",
    name: "REST API",
    desc: "POST /v1/chat",
    meta: "bearer key",
    status: "live",
  },
  {
    id: "slack",
    name: "Slack",
    desc: "/ask slash command",
    meta: "not configured",
    status: "off",
  },
  {
    id: "discord",
    name: "Discord",
    desc: "Server bot",
    meta: "not configured",
    status: "off",
  },
];

export const chatMessages: ChatMessage[] = [
  {
    id: "m1",
    role: "user",
    text: "What changed in the incident response process?",
  },
  {
    id: "m2",
    role: "assistant",
    text: "The escalation window moved to 15 minutes for P1 incidents, and on-call owners now attach a customer impact summary before the postmortem is opened.",
    sources: ["Engineering Docs", "Company Wiki"],
  },
];

export const chatSuggestions: ChatSuggestion[] = [
  {
    id: "coverage",
    label: "Show source coverage",
    answer:
      "Company Wiki has the broadest coverage with 8,240 indexed documents. Engineering Docs is currently syncing and has 5,870 documents available for retrieval.",
    sources: ["Company Wiki", "Engineering Docs"],
  },
  {
    id: "stale",
    label: "Find stale sources",
    answer:
      "Support KB is idle and Product Notion is in an error state. The next best action is to rescan Product Notion and review connector credentials if the scan fails again.",
    sources: ["Support KB", "Product Notion"],
  },
  {
    id: "handoff",
    label: "Draft an onboarding answer",
    answer:
      "New teammates should start with Company Wiki for policy basics, then use Engineering Docs for service ownership and runbooks. HR & Policies covers benefits and time-off questions.",
    sources: ["Company Wiki", "HR & Policies", "Engineering Docs"],
  },
];

export const apiKeys: ApiKey[] = [
  {
    id: "production",
    name: "Production",
    value: "pk_live_••••••••••••8f2a",
    lastUsed: "used 2m ago",
  },
  {
    id: "staging",
    name: "CI / staging",
    value: "pk_test_••••••••••••1c07",
    lastUsed: "used 4d ago",
  },
];

export const sessions: Session[] = [
  {
    id: "macbook",
    device: "MacBook Pro · Istanbul",
    detail: "Chrome · this device",
    current: true,
  },
  {
    id: "iphone",
    device: "iPhone · Telegram bot",
    detail: "last active 6h ago",
    current: false,
  },
];
