"use client";

import { Bot } from "lucide-react";
import { Card, SectionHeader } from "@/components/ui/card";
import { StatusPill } from "@/components/ui/status-pill";
import { Toggle } from "@/components/ui/toggle";
import { useChannels } from "@/hooks/use-console-data";

export function ChannelsPage() {
  const { channels, toggleChannel } = useChannels();

  return (
    <div className="mx-auto max-w-[1080px]">
      <SectionHeader
        title="Channels & bots"
        description="One knowledge base, many surfaces. Flip a channel on and it answers there instantly - same index, same citations."
      />
      <div className="grid gap-4 min-[720px]:grid-cols-2 min-[1000px]:grid-cols-3">
        {channels.map((channel) => (
          <Card key={channel.id} className="p-5">
            <div className="flex items-center justify-between">
              <span className="flex h-[42px] w-[42px] items-center justify-center rounded-[11px] border border-[#dde5f3] bg-[#eef2fa] text-primary">
                <Bot size={19} />
              </span>
              <StatusPill status={channel.status} />
            </div>
            <div className="mt-4 font-display text-[16.5px] font-semibold text-foreground">
              {channel.name}
            </div>
            <div className="mt-1 text-[13px] text-muted">{channel.desc}</div>
            <div className="mt-4 flex items-center justify-between border-t border-[#f2f4f9] pt-4">
              <span className="font-mono text-[11.5px] text-muted-soft">
                {channel.meta}
              </span>
              <Toggle
                checked={channel.status === "live"}
                label={`Toggle ${channel.name}`}
                onChange={() => toggleChannel(channel.id)}
              />
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}
