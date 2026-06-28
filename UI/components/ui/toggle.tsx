"use client";

import { cn } from "@/lib/cn";

export function Toggle({
  checked,
  onChange,
  label,
}: {
  checked: boolean;
  onChange: () => void;
  label: string;
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      aria-label={label}
      onClick={onChange}
      className={cn(
        "inline-flex h-[22px] w-[38px] items-center rounded-[11px] p-0.5 transition-colors",
        checked ? "justify-end bg-success" : "justify-start bg-[#d3dae6]",
      )}
    >
      <span className="h-[18px] w-[18px] rounded-full bg-white shadow-[0_1px_2px_rgba(0,0,0,.2)]" />
    </button>
  );
}
