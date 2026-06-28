import { Check } from "lucide-react";
import Image from "next/image";
import Link from "next/link";

type AuthMode = "login" | "register";

const panelCopy: Record<
  AuthMode,
  { kicker: string; title: string; bullets: string[] }
> = {
  login: {
    kicker: "WELCOME BACK",
    title: "Talk to your knowledge, on your stack.",
    bullets: [
      "Grounded answers with real source citations",
      "Chat from Teams, Telegram, Slack or the web",
      "One workspace across every connected source",
    ],
  },
  register: {
    kicker: "GET STARTED",
    title: "Stand up your own knowledge base in minutes.",
    bullets: [
      "Bring your own models, vectors and data sources",
      "Self-hosted - your data never leaves your network",
      "Free and open source, forever",
    ],
  },
};

export function AuthShell({
  children,
  mode = "login",
}: {
  children: React.ReactNode;
  mode?: AuthMode;
}) {
  const panel = panelCopy[mode];

  return (
    <div className="flex min-h-screen bg-background text-muted max-[899px]:flex-col">
      <aside className="relative flex w-[46%] flex-none overflow-hidden bg-navy px-12 py-11 max-[899px]:min-h-[240px] max-[899px]:w-full max-[899px]:px-6 max-[899px]:py-7">
        <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,.055)_1px,transparent_1px)] [background-size:24px_24px]" />
        <div className="relative flex min-h-full w-full flex-col">
          <Link href="/dashboard" className="flex items-center gap-2.5">
            <Image
              src="/pegadocs-mark-white.png"
              alt="PegaDocs"
              width={34}
              height={34}
              className="rounded-md"
              priority
            />
            <span className="font-display text-xl font-bold text-white">
              PegaDocs
            </span>
          </Link>

          <div className="my-auto max-w-[390px] py-12 max-[899px]:py-8">
            <div className="font-mono text-[12.5px] tracking-[.08em] text-[#7f93bd]">
              {panel.kicker}
            </div>
            <h1 className="mt-3.5 font-display text-[34px] font-bold leading-[1.15] text-white max-[520px]:text-[28px]">
              {panel.title}
            </h1>
            <div className="mt-7 flex flex-col gap-3.5">
              {panel.bullets.map((bullet) => (
                <div key={bullet} className="flex items-start gap-3">
                  <span className="mt-0.5 flex h-[22px] w-[22px] flex-none items-center justify-center rounded-md border border-white/15 bg-white/10 text-[#8fb0ee]">
                    <Check size={13} strokeWidth={3} />
                  </span>
                  <span className="text-[14.5px] leading-6 text-[#c3cfe6]">
                    {bullet}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex items-center gap-2.5 font-mono text-[11.5px] text-[#7281a0]">
            <span className="h-[7px] w-[7px] rounded-full bg-[#3ad08a]" />
            open source · self-hosted · apache-2.0
          </div>
        </div>
      </aside>

      <main className="flex min-w-0 flex-1 items-center justify-center px-7 py-10 max-[520px]:px-4">
        <div className="w-full max-w-[392px] animate-pd-rise">{children}</div>
      </main>
    </div>
  );
}
