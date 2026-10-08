import type { PortfolioSummary } from "@pocketorbit/types";
import { redirect } from "next/navigation";

import { demoPortfolio } from "./demo-data";
import { getInternalApiUrl } from "@/lib/internal-api-url";
import { getServerSessionCookieHeader } from "@/lib/server-session-cookie";

export async function getPortfolioSummary(): Promise<PortfolioSummary> {
  const apiUrl = getInternalApiUrl();
  if (!apiUrl) {
    if (process.env.NODE_ENV === "production") {
      throw new Error("Portfolio data is unavailable because API_INTERNAL_URL is not configured.");
    }
    return demoPortfolio;
  }

  try {
    const cookieHeader = await getServerSessionCookieHeader();
    const headers = cookieHeader ? { cookie: cookieHeader } : undefined;
    const response = await fetch(`${apiUrl}/portfolios`, {
      cache: "no-store",
      headers,
      signal: AbortSignal.timeout(5000)
    });
    if (response.status === 401) {
      // Keep the explicitly advertised guest demo, but never replace an expired
      // signed-in session with sample balances.
      if (process.env.NODE_ENV === "production" && cookieHeader) redirect("/login");
      return demoPortfolio;
    }
    if (!response.ok) throw new Error("Your portfolio could not be loaded. Try again shortly.");

    const portfolios = (await response.json()) as { id: string }[];
    if (!portfolios.length) {
      throw new Error("This account has no saved portfolio. Contact support to restore access.");
    }
    const summary = await fetch(
      `${apiUrl}/portfolios/${encodeURIComponent(portfolios[0].id)}/summary`,
      { cache: "no-store", headers, signal: AbortSignal.timeout(5000) }
    );
    if (
      summary.status === 401 &&
      process.env.NODE_ENV === "production" &&
      cookieHeader
    ) {
      redirect("/login");
    }
    if (!summary.ok) throw new Error("Your portfolio could not be loaded. Try again shortly.");
    return (await summary.json()) as PortfolioSummary;
  } catch (error) {
    if (process.env.NODE_ENV === "production") throw error;
    return demoPortfolio;
  }
}
