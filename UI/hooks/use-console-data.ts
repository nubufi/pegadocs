"use client";

import { useMemo, useState } from "react";
import {
  activity,
  apiKeys,
  channels as initialChannels,
  chatMessages as initialMessages,
  chatSuggestions,
  dataSources,
  knowledgeBases as initialKnowledgeBases,
  metrics,
  modelProviders as initialModelProviders,
  sessions,
  vectorStores as initialVectorStores,
} from "@/lib/mock/console";
import type {
  DataSource,
  KnowledgeBase,
  ModelProvider,
  VectorStore,
} from "@/types/console";

export function useDashboardData() {
  return {
    metrics,
    activity,
    knowledgeBases: initialKnowledgeBases,
  };
}

export function useCollections() {
  const [collections, setCollections] = useState(initialKnowledgeBases);

  function addCollection(input: Pick<KnowledgeBase, "name" | "description">) {
    const id = input.name.toLowerCase().replace(/[^a-z0-9]+/g, "-");
    setCollections((current) => [
      {
        id,
        name: input.name,
        sources: "No sources",
        vectors: "pending",
        docs: "0",
        status: "idle",
        description: input.description,
      },
      ...current,
    ]);
  }

  function deleteCollection(id: string) {
    setCollections((current) => current.filter((item) => item.id !== id));
  }

  return { collections, addCollection, deleteCollection };
}

export function useCollection(id: string) {
  const collection =
    initialKnowledgeBases.find((item) => item.id === id) ?? initialKnowledgeBases[0];
  const sources = dataSources.filter(
    (source) => source.collectionId === collection.id,
  );

  return { collection, sources };
}

export function useModelProviders() {
  const [providers, setProviders] = useState(initialModelProviders);

  function addProvider(input: Pick<ModelProvider, "name" | "kind" | "model">) {
    const tag = input.name
      .split(" ")
      .map((part) => part[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();

    setProviders((current) => [
      {
        id: input.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        tag,
        status: "idle",
        ...input,
      },
      ...current,
    ]);
  }

  return { providers, addProvider };
}

export function useVectorStores() {
  const [stores, setStores] = useState(initialVectorStores);

  function addStore(input: Pick<VectorStore, "name" | "detail">) {
    setStores((current) => [
      {
        id: input.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        chunks: "0",
        status: "idle",
        ...input,
      },
      ...current,
    ]);
  }

  return { stores, addStore };
}

export function useDataSources(collectionId?: string) {
  const [sources, setSources] = useState(dataSources);
  const visibleSources = useMemo(
    () =>
      collectionId
        ? sources.filter((source) => source.collectionId === collectionId)
        : sources,
    [collectionId, sources],
  );

  function addSource(
    input: Pick<DataSource, "name" | "type" | "scope"> & { collectionId?: string },
  ) {
    setSources((current) => [
      {
        id: input.name.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
        collectionId: input.collectionId ?? collectionId ?? "company-wiki",
        docs: "0",
        status: "syncing",
        name: input.name,
        type: input.type,
        scope: input.scope,
      },
      ...current,
    ]);
  }

  return { sources: visibleSources, addSource };
}

export function useChannels() {
  const [channels, setChannels] = useState(initialChannels);

  function toggleChannel(id: string) {
    setChannels((current) =>
      current.map((channel) =>
        channel.id === id
          ? { ...channel, status: channel.status === "live" ? "off" : "live" }
          : channel,
      ),
    );
  }

  return { channels, toggleChannel };
}

export function useChatPlayground() {
  const [messages, setMessages] = useState(initialMessages);
  const [usedSuggestions, setUsedSuggestions] = useState<string[]>([]);
  const [isTyping, setIsTyping] = useState(false);

  const suggestions = chatSuggestions.filter(
    (suggestion) => !usedSuggestions.includes(suggestion.id),
  );

  function appendAssistant(text: string, sources: string[]) {
    setMessages((current) => [
      ...current,
      {
        id: `a-${Date.now()}`,
        role: "assistant",
        text,
        sources,
      },
    ]);
  }

  function ask(text: string) {
    if (!text.trim() || isTyping) return;
    setMessages((current) => [
      ...current,
      { id: `u-${Date.now()}`, role: "user", text },
    ]);
    setIsTyping(true);
    window.setTimeout(() => {
      appendAssistant(
        "I checked the indexed sources and found the most relevant answer with citations. In API mode this response will stream token-by-token from the selected model.",
        ["Company Wiki", "Engineering Docs"],
      );
      setIsTyping(false);
    }, 850);
  }

  function askSuggestion(id: string) {
    const suggestion = chatSuggestions.find((item) => item.id === id);
    if (!suggestion || isTyping) return;
    setUsedSuggestions((current) => [...current, id]);
    setMessages((current) => [
      ...current,
      { id: `u-${id}`, role: "user", text: suggestion.label },
    ]);
    setIsTyping(true);
    window.setTimeout(() => {
      appendAssistant(suggestion.answer, suggestion.sources);
      setIsTyping(false);
    }, 700);
  }

  return { messages, suggestions, isTyping, ask, askSuggestion };
}

export function useAccountData() {
  return {
    profile: {
      name: "Nuri Bugra",
      email: "nuri@acme-corp.com",
      workspace: "acme-corp",
      timezone: "Europe/Istanbul (GMT+3)",
      initials: "NB",
    },
    apiKeys,
    sessions,
  };
}
