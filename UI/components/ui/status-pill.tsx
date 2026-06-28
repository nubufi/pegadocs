import { cn } from "@/lib/cn";
import type { Status } from "@/types/console";

const statusMap: Record<Status, { label: string; color: string; bg: string }> = {
  active: { label: "Active", color: "text-success", bg: "bg-success-bg" },
  live: { label: "Live", color: "text-success", bg: "bg-success-bg" },
  syncing: { label: "Syncing", color: "text-warning", bg: "bg-warning-bg" },
  idle: { label: "Idle", color: "text-idle", bg: "bg-idle-bg" },
  off: { label: "Off", color: "text-idle", bg: "bg-idle-bg" },
  error: { label: "Error", color: "text-error", bg: "bg-error-bg" },
};

export function StatusPill({
  status,
  label,
}: {
  status: Status;
  label?: string;
}) {
  const config = statusMap[status];

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 whitespace-nowrap rounded-md px-2.5 py-1 font-mono text-[11px] font-semibold",
        config.color,
        config.bg,
      )}
    >
      <span
        className={cn(
          "h-1.5 w-1.5 rounded-full bg-current",
          status === "syncing" && "animate-pd-spin rounded-[2px]",
        )}
      />
      {label ?? config.label}
    </span>
  );
}
