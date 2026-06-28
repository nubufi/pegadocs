export const integrationGroups = [
  {
    title: "Model providers",
    sub: "llm · embeddings",
    items: [
      "OpenRouter",
      "OpenAI",
      "Anthropic",
      "AWS Bedrock",
      "Azure OpenAI",
      "Google Vertex",
      "Ollama",
      "Groq",
    ],
  },
  {
    title: "Vector stores",
    sub: "retrieval",
    items: ["Pinecone", "pgvector", "Qdrant", "Weaviate", "Milvus", "Chroma"],
  },
  {
    title: "Data sources",
    sub: "ingest · sync",
    items: [
      "SharePoint",
      "Amazon S3",
      "Google Drive",
      "Confluence",
      "Notion",
      "Postgres",
      "GitHub",
      "Web crawler",
    ],
  },
  {
    title: "Channels",
    sub: "chat surfaces",
    items: [
      "Web widget",
      "Microsoft Teams",
      "Telegram",
      "Slack",
      "Discord",
      "REST API",
    ],
  },
];

export const features = [
  {
    icon: "BYO",
    title: "Bring your own models",
    body: "Mix and match LLM and embedding providers per knowledge base. Swap them without re-indexing your data.",
  },
  {
    icon: "</>",
    title: "Source-grounded answers",
    body: "Every response cites the documents it used, so your team can trust and verify what the assistant says.",
  },
  {
    icon: "API",
    title: "Multi-channel bots",
    body: "One knowledge base, many surfaces. Web, Teams, Telegram, Slack and a REST API, all in sync.",
  },
  {
    icon: "{}",
    title: "Declarative config",
    body: "Describe providers, vectors, sources and channels in a single YAML file. Version it, review it, ship it.",
  },
  {
    icon: "SEC",
    title: "Self-hosted and private",
    body: "Runs entirely in your environment. No data leaves your network, no third-party account required.",
  },
  {
    icon: "EXT",
    title: "Pluggable adapters",
    body: "A thin adapter interface for every layer means new providers and sources are quick to add and community-owned.",
  },
];

export const pipelineSteps = [
  {
    eyebrow: "01",
    title: "Connect models",
    body: "Point at any LLM and embedding provider: OpenRouter, Bedrock, Azure OpenAI. Your keys, hot-swappable.",
    icon: "model",
  },
  {
    eyebrow: "02",
    title: "Attach vector store",
    body: "Bring Pinecone, pgvector, Qdrant or Weaviate. PegaDocs handles chunking, indexing and retrieval.",
    icon: "vector",
  },
  {
    eyebrow: "03",
    title: "Sync data sources",
    body: "Connect SharePoint, S3 buckets, Confluence or Postgres. Scheduled syncs keep answers fresh.",
    icon: "source",
  },
  {
    eyebrow: "04",
    title: "Chat anywhere",
    body: "Talk to it from a web widget, Microsoft Teams, Telegram or Slack with grounded, cited answers.",
    icon: "chat",
    dark: true,
  },
];

export const trustItems = [
  "OpenRouter",
  "AWS Bedrock",
  "Azure OpenAI",
  "Pinecone",
  "pgvector",
  "SharePoint",
  "Amazon S3",
];
