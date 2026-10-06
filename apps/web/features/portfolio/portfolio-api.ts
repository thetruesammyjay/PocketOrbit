import type { PortfolioSummary } from "@pocketorbit/types";

import { demoPortfolio } from "./demo-data";

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const apiUrl = process.env.NEXT_PUBLIC_API_URL;
  if (!apiUrl) return demoPortfolio;

  try {
    const response = await fetch(`${apiUrl.replace(/\/$/, "")}/portfolios/demo/summary`, {
      cache: "no-store",
      signal: AbortSignal.timeout(1200)
    });
    if (!response.ok) return demoPortfolio;
    return (await response.json()) as PortfolioSummary;
  } catch {
    return demoPortfolio;
  }
}
