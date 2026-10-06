import type { ReactNode } from "react";

import { AppShell } from "@/components/app-shell";

export default function PortfolioLayout({ children }: Readonly<{ children: ReactNode }>) {
  return <AppShell>{children}</AppShell>;
}
