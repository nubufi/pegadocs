import { cn } from "@/lib/cn";

export function DataTable<T>({
  columns,
  rows,
  getKey,
  className,
}: {
  columns: { key: string; label: string; render: (row: T) => React.ReactNode }[];
  rows: T[];
  getKey: (row: T) => string;
  className?: string;
}) {
  const template = `repeat(${columns.length}, minmax(130px, 1fr))`;

  return (
    <div
      className={cn(
        "overflow-x-auto rounded-[14px] border border-border bg-white",
        className,
      )}
    >
      <div className="min-w-[760px]">
        <div
          className="grid gap-3 border-b border-[#eef1f7] bg-[#f7f9fc] px-5 py-3 font-mono text-[11px] uppercase tracking-[.04em] text-muted-soft"
          style={{ gridTemplateColumns: template }}
        >
          {columns.map((column) => (
            <div key={column.key}>{column.label}</div>
          ))}
        </div>
        {rows.map((row) => (
          <div
            key={getKey(row)}
            className="grid items-center gap-3 border-b border-[#f2f4f9] px-5 py-4 last:border-b-0"
            style={{ gridTemplateColumns: template }}
          >
            {columns.map((column) => (
              <div key={column.key}>{column.render(row)}</div>
            ))}
          </div>
        ))}
      </div>
    </div>
  );
}
