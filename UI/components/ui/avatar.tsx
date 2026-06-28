import { cn } from "@/lib/cn";

export function Avatar({
  initials,
  size = "md",
  className,
}: {
  initials: string;
  size?: "sm" | "md" | "lg";
  className?: string;
}) {
  return (
    <span
      className={cn(
        "inline-flex flex-none items-center justify-center bg-primary font-semibold text-white",
        size === "sm" && "h-[34px] w-[34px] rounded-full text-[13px]",
        size === "md" && "h-12 w-12 rounded-xl text-base",
        size === "lg" && "h-[72px] w-[72px] rounded-[18px] font-display text-[28px] font-bold",
        className,
      )}
    >
      {initials}
    </span>
  );
}
