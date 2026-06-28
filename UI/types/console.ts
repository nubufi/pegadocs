export type Status = "active" | "live" | "syncing" | "idle" | "off" | "error";

export type Metric = {
  label: string;
  value: string;
  sub: string;
};

export type ActivityItem = {
  text: string;
  time: string;
};

export type KnowledgeBase = {
  id: string;
  name: string;
  sources: string;
  vectors: string;
  docs: string;
  status: Status;
  description: string;
};

export type ModelProvider = {
  id: string;
  name: string;
  tag: string;
  kind: string;
  model: string;
  status: Status;
};

export type VectorStore = {
  id: string;
  name: string;
  detail: string;
  chunks: string;
  status: Status;
};

export type DataSource = {
  id: string;
  collectionId: string;
  name: string;
  type: string;
  scope: string;
  docs: string;
  status: Status;
};

export type Channel = {
  id: string;
  name: string;
  desc: string;
  meta: string;
  status: Status;
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  text: string;
  sources?: string[];
};

export type ChatSuggestion = {
  id: string;
  label: string;
  answer: string;
  sources: string[];
};

export type ApiKey = {
  id: string;
  name: string;
  value: string;
  lastUsed: string;
};

export type Session = {
  id: string;
  device: string;
  detail: string;
  current: boolean;
};
