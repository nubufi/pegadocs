"use client";

import { Send } from "lucide-react";
import { FormEvent, useState } from "react";
import { Button } from "@/components/ui/button";
import { useChatPlayground } from "@/hooks/use-console-data";
import { cn } from "@/lib/cn";

export function ChatPage() {
  const { messages, suggestions, isTyping, ask, askSuggestion } =
    useChatPlayground();
  const [value, setValue] = useState("");

  function submit(event: FormEvent) {
    event.preventDefault();
    ask(value);
    setValue("");
  }

  return (
    <div className="mx-auto max-w-[960px]">
      <div className="mb-4 flex flex-wrap items-center gap-3">
        <span className="text-[13px] text-muted-soft">Knowledge base:</span>
        <span className="inline-flex items-center gap-2 rounded-[9px] border border-[#dde5f3] bg-white px-3 py-2 text-[13.5px] font-semibold text-primary">
          Company Wiki
        </span>
        <span className="font-mono text-xs text-muted-soft">
          model: claude-3.5-sonnet · pinecone://prod-kb
        </span>
      </div>
      <div className="overflow-hidden rounded-2xl border border-[#1c2c47] bg-navy shadow-chat">
        <div
          data-scroll
          className="flex min-h-[340px] max-h-[440px] flex-col gap-4 overflow-y-auto p-5 md:p-6"
        >
          {messages.map((message) => (
            <div
              key={message.id}
              className={cn(
                "flex",
                message.role === "user" ? "justify-end" : "justify-start",
              )}
            >
              <div
                className={cn(
                  "max-w-[78%] text-sm leading-6",
                  message.role === "user"
                    ? "rounded-[13px_13px_4px_13px] bg-primary-hover px-4 py-3 text-white"
                    : "rounded-[4px_13px_13px_13px] border border-white/[.09] bg-white/[.06] px-4 py-3 text-[#dde6f5]",
                )}
              >
                {message.text}
                {message.sources?.length ? (
                  <div className="mt-3 flex flex-wrap gap-2">
                    {message.sources.map((source) => (
                      <span
                        key={source}
                        className="inline-flex items-center gap-1.5 rounded-md border border-white/[.12] bg-white/[.06] px-2 py-1 font-mono text-[10.5px] text-[#9fb9ea]"
                      >
                        <span className="h-[5px] w-[5px] rounded-full bg-[#6f9aea]" />
                        {source}
                      </span>
                    ))}
                  </div>
                ) : null}
              </div>
            </div>
          ))}
          {isTyping ? (
            <div className="flex justify-start">
              <div className="flex items-center gap-1 rounded-[4px_13px_13px_13px] border border-white/[.09] bg-white/[.06] px-4 py-3">
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-[#7b8aab]" />
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-[#7b8aab] [animation-delay:.2s]" />
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-[#7b8aab] [animation-delay:.4s]" />
              </div>
            </div>
          ) : null}
        </div>
        <div className="border-t border-[#1c2c47] bg-footer-navy p-4">
          <div className="mb-3 flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
              <button
                key={suggestion.id}
                type="button"
                onClick={() => askSuggestion(suggestion.id)}
                className="rounded-lg border border-white/[.12] bg-white/[.06] px-3 py-1.5 text-[12.5px] font-medium text-[#aebbd6] transition-colors hover:bg-white/[.12]"
              >
                {suggestion.label}
              </button>
            ))}
          </div>
          <form
            onSubmit={submit}
            className="flex items-center gap-3 rounded-[10px] border border-white/[.12] bg-white/[.06] px-3 py-2"
          >
            <input
              value={value}
              onChange={(event) => setValue(event.target.value)}
              placeholder="Message your knowledge base..."
              className="min-w-0 flex-1 bg-transparent text-sm text-white outline-none placeholder:text-[#7b8aab]"
            />
            <Button
              type="submit"
              size="icon"
              className="h-8 w-8 rounded-lg bg-primary-hover shadow-none"
              disabled={!value.trim() || isTyping}
              aria-label="Send message"
            >
              <Send size={16} />
            </Button>
          </form>
        </div>
      </div>
    </div>
  );
}
