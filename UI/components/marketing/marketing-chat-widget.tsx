"use client";

import Image from "next/image";
import { ArrowRight } from "lucide-react";
import { useEffect, useRef, useState } from "react";

type Message = {
  role: "assistant" | "user";
  text: string;
  sources?: string[];
};

const initialMessages: Message[] = [
  {
    role: "assistant",
    text: "Hi. Ask me anything about your connected knowledge bases. I answer with the exact sources I used.",
  },
  {
    role: "user",
    text: "Which vector store is prod using?",
  },
  {
    role: "assistant",
    text: "Production runs on Pinecone with text-embedding-3-large served through Azure OpenAI.",
    sources: ["config > pegadocs.yaml"],
  },
];

const suggestions = {
  sso: {
    label: "Where's SSO documented?",
    answer:
      "SSO setup lives in the Platform Admin guide. SAML and OIDC are both supported, with group-to-role mapping under Settings.",
    sources: ["sharepoint > IT-Policies/SSO.docx", "confluence > Platform/Auth"],
  },
  onboard: {
    label: "Summarize Q3 onboarding changes",
    answer:
      "Three changes in Q3: laptop provisioning moved to self-service, security training is mandatory in week one, and benefits enrollment closes on day 30.",
    sources: ["s3 > hr-docs/onboarding-q3.pdf"],
  },
  bots: {
    label: "How do I add a Teams bot?",
    answer:
      "Register an Azure Bot resource, add its app ID and secret to channels.teams, then redeploy. The same knowledge base answers in Teams.",
    sources: ["github > docs/channels/teams.md"],
  },
};

type SuggestionKey = keyof typeof suggestions;

export function MarketingChatWidget() {
  const [messages, setMessages] = useState<Message[]>(initialMessages);
  const [typing, setTyping] = useState(false);
  const [asked, setAsked] = useState<Record<string, boolean>>({});
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, typing]);

  const ask = (key: SuggestionKey) => {
    const item = suggestions[key];
    if (!item || typing) return;

    setAsked((current) => ({ ...current, [key]: true }));
    setMessages((current) => [
      ...current,
      { role: "user", text: item.label },
    ]);
    setTyping(true);

    window.setTimeout(() => {
      setMessages((current) => [
        ...current,
        {
          role: "assistant",
          text: item.answer,
          sources: item.sources,
        },
      ]);
      setTyping(false);
    }, 900);
  };

  const availableSuggestions = Object.entries(suggestions).filter(
    ([key]) => !asked[key],
  ) as [SuggestionKey, (typeof suggestions)[SuggestionKey]][];

  return (
    <div className="animate-pd-float">
      <div className="overflow-hidden rounded-[18px] border border-[#e4e9f2] bg-white shadow-card-hero">
        <div className="flex items-center gap-3 border-b border-[#eef1f7] bg-white px-4 py-3.5">
          <span className="flex h-[34px] w-[34px] items-center justify-center rounded-[9px] bg-primary">
            <Image
              src="/pegadocs-mark-white.png"
              alt=""
              width={24}
              height={24}
              className="h-6 w-6 object-contain"
            />
          </span>
          <div className="leading-tight">
            <div className="text-[14.5px] font-semibold text-foreground">
              PegaDocs Assistant
            </div>
            <div className="font-mono text-[11.5px] font-semibold text-success">
              grounded · 3 sources
            </div>
          </div>
          <div className="flex-1" />
          <span className="hidden font-mono text-[11px] text-muted-soft sm:inline">
            teams · web · telegram
          </span>
        </div>

        <div
          ref={scrollRef}
          data-scroll
          className="flex max-h-[330px] min-h-[268px] flex-col gap-3.5 overflow-y-auto bg-[#fafbfd] px-4 py-4"
        >
          {messages.map((message, index) =>
            message.role === "user" ? (
              <div key={`${message.text}-${index}`} className="flex justify-end">
                <div className="max-w-[80%] rounded-[13px_13px_4px_13px] bg-primary px-3.5 py-2.5 text-sm text-white">
                  {message.text}
                </div>
              </div>
            ) : (
              <div key={`${message.text}-${index}`} className="flex gap-2.5">
                <span className="mt-0.5 flex h-[26px] w-[26px] flex-none items-center justify-center rounded-[7px] bg-primary">
                  <Image
                    src="/pegadocs-mark-white.png"
                    alt=""
                    width={18}
                    height={18}
                    className="h-[18px] w-[18px] object-contain"
                  />
                </span>
                <div className="max-w-[84%]">
                  <div className="rounded-[4px_13px_13px_13px] border border-[#eaeef5] bg-white px-3.5 py-2.5 text-sm text-[#33415c]">
                    {message.text}
                  </div>
                  {message.sources?.length ? (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {message.sources.map((source) => (
                        <span
                          key={source}
                          className="inline-flex items-center gap-1.5 rounded-md border border-[#dde5f3] bg-[#eef2fa] px-2 py-1 font-mono text-[10.5px] text-primary"
                        >
                          <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                          {source}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
              </div>
            ),
          )}

          {typing ? (
            <div className="flex gap-2.5">
              <span className="flex h-[26px] w-[26px] flex-none items-center justify-center rounded-[7px] bg-primary">
                <Image
                  src="/pegadocs-mark-white.png"
                  alt=""
                  width={18}
                  height={18}
                  className="h-[18px] w-[18px] object-contain"
                />
              </span>
              <div className="flex items-center gap-1 rounded-[4px_13px_13px_13px] border border-[#eaeef5] bg-white px-3.5 py-3">
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-muted-soft" />
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-muted-soft [animation-delay:.2s]" />
                <span className="h-1.5 w-1.5 animate-pd-blink rounded-full bg-muted-soft [animation-delay:.4s]" />
              </div>
            </div>
          ) : null}
        </div>

        <div className="border-t border-[#eef1f7] bg-white px-3.5 py-3">
          <div className="mb-3 flex flex-wrap gap-2">
            {availableSuggestions.map(([key, item]) => (
              <button
                key={key}
                type="button"
                onClick={() => ask(key)}
                className="rounded-lg border border-[#e2e8f2] bg-[#f3f6fb] px-3 py-1.5 text-[12.5px] font-medium text-primary transition-colors hover:border-[#c9d5ec] hover:bg-[#e9eef8]"
              >
                {item.label}
              </button>
            ))}
          </div>
          <div className="flex items-center gap-2.5 rounded-[10px] border border-[#e6ebf3] bg-[#f7f9fc] px-3 py-2">
            <span className="flex-1 text-sm text-muted-soft">
              Ask about your knowledge base...
            </span>
            <span className="flex h-[30px] w-[30px] items-center justify-center rounded-lg bg-primary text-white">
              <ArrowRight size={15} strokeWidth={2.4} />
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}
