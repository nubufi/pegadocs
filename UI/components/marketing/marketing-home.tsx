import Image from "next/image";
import Link from "next/link";
import {
  ArrowRight,
  Check,
  Cpu,
  Database,
  MessageCircle,
  PackageOpen,
} from "lucide-react";
import { Card } from "@/components/ui/card";
import { GitHubIcon } from "@/components/ui/github-icon";
import { cn } from "@/lib/cn";
import {
  features,
  integrationGroups,
  pipelineSteps,
  trustItems,
} from "./marketing-data";
import { MarketingChatWidget } from "./marketing-chat-widget";

const githubUrl = "https://github.com/nubufi/pegadocs";

function PipelineIcon({ icon, dark }: { icon: string; dark?: boolean }) {
  const className = "h-[22px] w-[22px]";
  const icons = {
    model: <Cpu className={className} strokeWidth={1.9} />,
    vector: <Database className={className} strokeWidth={1.9} />,
    source: <PackageOpen className={className} strokeWidth={1.9} />,
    chat: <MessageCircle className={className} strokeWidth={1.9} />,
  };

  return (
    <div
      className={cn(
        "flex h-[46px] w-[46px] items-center justify-center rounded-[11px] border",
        dark
          ? "border-white/20 bg-white/10 text-white"
          : "border-[#dde5f3] bg-[#eef2fa] text-primary",
      )}
    >
      {icons[icon as keyof typeof icons]}
    </div>
  );
}

function SectionIntro({
  eyebrow,
  title,
  body,
  centered = false,
}: {
  eyebrow: string;
  title: string;
  body?: string;
  centered?: boolean;
}) {
  return (
    <div className={cn("max-w-[640px]", centered && "mx-auto text-center")}>
      <div className="font-mono text-[12.5px] font-semibold tracking-[.08em] text-primary">
        {eyebrow}
      </div>
      <h2 className="mt-3.5 font-display text-[34px] font-bold leading-[1.08] tracking-normal text-foreground sm:text-[40px]">
        {title}
      </h2>
      {body ? (
        <p className="mt-4 text-[17px] leading-7 text-[#4a5973]">{body}</p>
      ) : null}
    </div>
  );
}

export function MarketingHome() {
  return (
    <main className="overflow-x-hidden bg-background text-[#41506b]">
      <header className="sticky top-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
        <nav className="mx-auto flex max-w-[1180px] items-center gap-6 px-5 py-3.5 sm:px-7">
          <Link href="#top" className="flex items-center gap-2.5">
            <Image
              src="/pegadocs-mark.png"
              alt="PegaDocs"
              width={34}
              height={34}
              className="h-[34px] w-[34px] object-contain"
              priority
            />
            <span className="font-display text-[19px] font-bold tracking-normal text-foreground">
              PegaDocs
            </span>
          </Link>
          <div className="flex-1" />
          <div className="hidden items-center gap-6 min-[760px]:flex">
            <a href="#how" className="text-[14.5px] font-medium text-[#41506b]">
              How it works
            </a>
            <a
              href="#integrations"
              className="text-[14.5px] font-medium text-[#41506b]"
            >
              Integrations
            </a>
            <a
              href="#features"
              className="text-[14.5px] font-medium text-[#41506b]"
            >
              Features
            </a>
            <a
              href="#quickstart"
              className="text-[14.5px] font-medium text-[#41506b]"
            >
              Self-host
            </a>
            <Link
              href="/dashboard"
              className="text-[14.5px] font-semibold text-primary"
            >
              Live demo
            </Link>
          </div>
          <Link
            href="/login"
            className="hidden text-[14.5px] font-semibold text-foreground sm:inline"
          >
            Sign in
          </Link>
          <a
            href={githubUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-[9px] border border-navy bg-navy px-3.5 py-2 text-sm font-semibold text-white"
          >
            <GitHubIcon className="h-4 w-4" />
            Star
          </a>
        </nav>
      </header>

      <section
        id="top"
        className="relative bg-background [background-image:radial-gradient(#dde4f0_1px,transparent_1px)] [background-size:26px_26px]"
      >
        <div className="absolute inset-0 bg-[radial-gradient(120%_80%_at_70%_0%,rgba(251,252,254,0)_40%,#fbfcfe_100%)]" />
        <div className="relative mx-auto grid max-w-[1180px] items-center gap-12 px-5 py-16 sm:px-7 lg:grid-cols-[1.05fr_.95fr] lg:gap-14 lg:py-20">
          <div>
            <div className="inline-flex items-center gap-2 rounded-full border border-[#e0e7f3] bg-white px-3 py-1.5 font-mono text-[12.5px] font-semibold tracking-[.01em] text-primary">
              <span className="h-[7px] w-[7px] animate-pd-pulse rounded-full bg-primary" />
              OPEN SOURCE · SELF-HOSTED RAG
            </div>
            <h1 className="mt-5 font-display text-[40px] font-bold leading-[1.04] tracking-normal text-foreground min-[480px]:text-[48px] min-[760px]:text-[60px]">
              Your knowledge base,
              <br />
              <span className="text-primary">on your stack.</span>
            </h1>
            <p className="mt-5 max-w-[480px] text-[19px] leading-[1.55] text-[#4a5973]">
              Bring your own models, vector stores, and data sources. PegaDocs
              turns SharePoint, S3, and Postgres into a grounded assistant you
              can talk to from Teams, Telegram, or a chat widget.
            </p>
            <div className="mt-8 flex flex-wrap gap-3.5">
              <a
                href="#quickstart"
                className="inline-flex h-[50px] items-center justify-center rounded-[11px] border border-transparent bg-primary px-6 text-[15.5px] font-semibold text-white shadow-button transition-colors hover:bg-primary-hover"
              >
                Deploy in 5 minutes
              </a>
              <a
                href={githubUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex h-[50px] items-center justify-center gap-2.5 rounded-[11px] border border-border-strong bg-white px-6 text-[15.5px] font-semibold text-foreground transition-colors hover:border-[#cdd8ec] hover:bg-[#f7f9fc]"
              >
                <GitHubIcon className="h-[18px] w-[18px]" />
                View on GitHub
              </a>
            </div>
            <div className="mt-9 flex flex-wrap gap-6 font-mono">
              {[
                ["20+", "PROVIDERS"],
                ["6", "VECTOR STORES"],
                ["5", "CHAT CHANNELS"],
              ].map(([value, label], index) => (
                <div key={label} className="flex items-stretch gap-6">
                  {index > 0 ? <div className="w-px bg-[#e4e9f2]" /> : null}
                  <div>
                    <div className="text-[23px] font-semibold text-foreground">
                      {value}
                    </div>
                    <div className="text-[12.5px] tracking-[.02em] text-idle">
                      {label}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <MarketingChatWidget />
        </div>
      </section>

      <div className="border-y border-[#eef1f7] bg-white">
        <div className="mx-auto flex max-w-[1180px] flex-wrap items-center justify-center gap-3 px-5 py-5 font-mono text-[12.5px] tracking-[.04em] text-muted-soft sm:gap-7 sm:px-7">
          <span className="text-idle">WORKS WITH</span>
          {trustItems.map((item, index) => (
            <span key={item} className="inline-flex items-center gap-3 sm:gap-7">
              <span>{item}</span>
              {index < trustItems.length - 1 ? (
                <span className="opacity-40">/</span>
              ) : null}
            </span>
          ))}
        </div>
      </div>

      <section id="how" className="bg-background px-5 py-[92px] sm:px-7">
        <div className="mx-auto max-w-[1180px]">
          <SectionIntro
            eyebrow="HOW IT WORKS"
            title="Four connections. One assistant."
            body="PegaDocs is the wiring between the tools you already run. Plug each layer in and it stays yours, in your cloud."
          />
          <div className="relative mt-14 grid gap-[18px] min-[900px]:grid-cols-4 sm:grid-cols-2">
            <div className="absolute left-[8%] right-[8%] top-[34px] z-0 hidden h-0.5 bg-[repeating-linear-gradient(90deg,#cdd8ec_0_7px,transparent_7px_14px)] min-[1024px]:block" />
            {pipelineSteps.map((step) => (
              <Card
                key={step.title}
                className={cn(
                  "relative z-10 rounded-[15px] border-[#e4e9f2] p-5",
                  step.dark &&
                    "border-primary bg-primary shadow-[0_18px_40px_-20px_rgba(27,58,124,.6)] hover:border-primary",
                )}
              >
                <PipelineIcon icon={step.icon} dark={step.dark} />
                <div
                  className={cn(
                    "mt-4 font-mono text-[11.5px]",
                    step.dark ? "text-[#a9bbe0]" : "text-muted-soft",
                  )}
                >
                  {step.eyebrow}
                </div>
                <h3
                  className={cn(
                    "mt-1 font-display text-[18.5px] font-semibold tracking-normal",
                    step.dark ? "text-white" : "text-foreground",
                  )}
                >
                  {step.title}
                </h3>
                <p
                  className={cn(
                    "mt-2 text-sm leading-6",
                    step.dark ? "text-[#cdd8ee]" : "text-muted",
                  )}
                >
                  {step.body}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section
        id="integrations"
        className="border-y border-[#e9edf5] bg-section px-5 py-[92px] sm:px-7"
      >
        <div className="mx-auto max-w-[1180px]">
          <SectionIntro
            centered
            eyebrow="INTEGRATIONS"
            title="Bring your own everything"
            body="No lock-in. Swap any layer without touching the rest. Don't see yours? It's a small adapter away."
          />
          <div className="mt-12 grid gap-[18px] min-[900px]:grid-cols-4 sm:grid-cols-2">
            {integrationGroups.map((group) => (
              <Card
                key={group.title}
                className="rounded-[15px] border-[#e4e9f2] p-5"
              >
                <div className="flex items-center gap-2.5">
                  <span className="h-2 w-2 rounded-sm bg-primary" />
                  <span className="font-display text-[15px] font-semibold tracking-normal text-foreground">
                    {group.title}
                  </span>
                </div>
                <div className="ml-[17px] mt-1 font-mono text-[11px] text-muted-soft">
                  {group.sub}
                </div>
                <div className="mt-4 flex flex-col gap-2">
                  {group.items.map((item) => (
                    <div
                      key={item}
                      className="flex items-center gap-2.5 rounded-lg border border-[#eaeef5] bg-[#f7f9fc] px-3 py-2"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-[#9fb0d4]" />
                      <span className="text-[13.5px] font-medium text-[#33415c]">
                        {item}
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="features" className="bg-background px-5 py-[92px] sm:px-7">
        <div className="mx-auto max-w-[1180px]">
          <SectionIntro
            eyebrow="FEATURES"
            title="Built for teams that run their own stack"
          />
          <div className="mt-11 grid gap-[18px] min-[900px]:grid-cols-3">
            {features.map((feature) => (
              <Card
                key={feature.title}
                className="rounded-[15px] border-[#e4e9f2] p-6"
              >
                <div className="flex h-[42px] w-[42px] items-center justify-center rounded-[10px] border border-[#dde5f3] bg-[#eef2fa] font-mono text-[15px] font-semibold text-primary">
                  {feature.icon}
                </div>
                <h3 className="mt-4 font-display text-lg font-semibold tracking-normal text-foreground">
                  {feature.title}
                </h3>
                <p className="mt-2 text-[14.5px] leading-6 text-muted">
                  {feature.body}
                </p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      <section id="quickstart" className="bg-background px-5 pb-[92px] sm:px-7">
        <div className="mx-auto grid max-w-[1180px] items-center gap-12 min-[900px]:grid-cols-[1fr_1.15fr]">
          <div>
            <SectionIntro
              eyebrow="SELF-HOST"
              title="Up and running in five minutes"
              body="One container, one config file. Runs on your laptop, a VM, or Kubernetes. Your data never leaves your network."
            />
            <div className="mt-6 flex flex-col gap-3">
              {[
                "100% open source, Apache-2.0 licensed",
                "No telemetry, no phone-home, no vendor account",
                "Single binary and Docker image, declarative YAML config",
              ].map((item) => (
                <div key={item} className="flex items-start gap-3">
                  <Check
                    className="mt-0.5 h-4 w-4 flex-none text-primary"
                    strokeWidth={2.2}
                  />
                  <span className="text-[15px] text-[#33415c]">{item}</span>
                </div>
              ))}
            </div>
          </div>

          <div className="overflow-hidden rounded-[15px] border border-[#1c2c47] bg-navy shadow-chat">
            <div className="flex items-center gap-2 border-b border-[#1c2c47] px-4 py-3">
              <span className="h-[11px] w-[11px] rounded-full bg-[#39496a]" />
              <span className="h-[11px] w-[11px] rounded-full bg-[#39496a]" />
              <span className="h-[11px] w-[11px] rounded-full bg-[#39496a]" />
              <span className="ml-2 font-mono text-xs text-[#7b8aab]">
                bash - pegadocs
              </span>
            </div>
            <pre className="m-0 overflow-x-auto p-5 font-mono text-[13px] leading-[1.85] text-[#c6d2ec]">
              <code>{`# clone and launch
git clone https://github.com/nubufi/pegadocs
cd pegadocs

# configure your providers in pegadocs.yaml
docker compose up -d

✓ models     azure-openai, bedrock
✓ vectors    pinecone://prod-kb
✓ sources    sharepoint, s3://hr-docs
✓ channels   web, teams, telegram

→ PegaDocs ready at http://localhost:8080`}</code>
            </pre>
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden bg-navy px-5 py-[88px] sm:px-7">
        <div className="absolute inset-0 bg-[radial-gradient(rgba(255,255,255,.06)_1px,transparent_1px)] [background-size:24px_24px] opacity-50" />
        <div className="relative mx-auto max-w-[880px] text-center">
          <Image
            src="/pegadocs-mark-white.png"
            alt=""
            width={64}
            height={64}
            className="mx-auto h-16 w-16 object-contain opacity-95"
          />
          <h2 className="mt-5 font-display text-[36px] font-bold leading-[1.08] tracking-normal text-white sm:text-[42px]">
            Open source. Built in the open.
          </h2>
          <p className="mx-auto mt-4 max-w-[560px] text-lg leading-7 text-[#aebbd6]">
            Star the repo, open an issue, or ship an adapter. PegaDocs is
            community-driven and self-hostable forever.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-3.5">
            <a
              href={githubUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-[50px] items-center gap-2.5 rounded-[11px] bg-white px-6 text-[15.5px] font-semibold text-navy"
            >
              <GitHubIcon className="h-[18px] w-[18px]" />
              Star on GitHub
            </a>
            <a
              href={`${githubUrl}#readme`}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex h-[50px] items-center gap-2 rounded-[11px] border border-white/30 px-6 text-[15.5px] font-semibold text-white"
            >
              Read the docs
              <ArrowRight size={16} />
            </a>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#1c2c47] bg-footer-navy px-5 py-10 sm:px-7">
        <div className="mx-auto grid max-w-[1180px] gap-8 min-[680px]:grid-cols-2 lg:grid-cols-[1.4fr_1fr_1fr_1fr]">
          <div>
            <div className="flex items-center gap-2.5">
              <Image
                src="/pegadocs-mark-white.png"
                alt=""
                width={30}
                height={30}
                className="h-[30px] w-[30px] object-contain"
              />
              <span className="font-display text-lg font-bold tracking-normal text-white">
                PegaDocs
              </span>
            </div>
            <p className="mt-3.5 max-w-[260px] text-[13.5px] leading-6 text-[#7b8aab]">
              The open-source knowledge base layer for your own models, vectors
              and data sources.
            </p>
          </div>
          {[
            {
              title: "PRODUCT",
              links: [
                ["How it works", "#how"],
                ["Integrations", "#integrations"],
                ["Features", "#features"],
                ["Self-host", "#quickstart"],
              ],
            },
            {
              title: "RESOURCES",
              links: [
                ["Documentation", `${githubUrl}#readme`],
                ["GitHub", githubUrl],
                ["Issues", `${githubUrl}/issues`],
                ["Changelog", `${githubUrl}/releases`],
              ],
            },
            {
              title: "COMMUNITY",
              links: [
                ["Discussions", `${githubUrl}/discussions`],
                ["Contributing", `${githubUrl}/blob/main/CONTRIBUTING.md`],
                ["License", `${githubUrl}/blob/main/LICENSE`],
              ],
            },
          ].map((group) => (
            <div key={group.title}>
              <div className="mb-3.5 font-mono text-[11.5px] tracking-[.06em] text-[#5f6f93]">
                {group.title}
              </div>
              <div className="flex flex-col gap-2.5">
                {group.links.map(([label, href]) => (
                  <a
                    key={label}
                    href={href}
                    className="text-sm text-[#aebbd6] transition-colors hover:text-white"
                    target={href.startsWith("http") ? "_blank" : undefined}
                    rel={
                      href.startsWith("http") ? "noopener noreferrer" : undefined
                    }
                  >
                    {label}
                  </a>
                ))}
              </div>
            </div>
          ))}
        </div>
        <div className="mx-auto mt-9 flex max-w-[1180px] flex-wrap justify-between gap-3.5 border-t border-[#1c2c47] pt-5 font-mono text-xs text-[#5f6f93]">
          <span>© 2026 PegaDocs · Apache-2.0</span>
          <span>self-hosted · grounded · yours</span>
        </div>
      </footer>
    </main>
  );
}
