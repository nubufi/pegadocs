import { ConsoleShell } from "@/components/console/console-shell";

export default function Layout({ children }: { children: React.ReactNode }) {
  return <ConsoleShell>{children}</ConsoleShell>;
}
