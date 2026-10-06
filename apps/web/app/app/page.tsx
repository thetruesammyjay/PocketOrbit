import { Dashboard } from "@/features/portfolio/dashboard";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function OverviewPage() {
  const portfolio = await getPortfolioSummary();
  return <Dashboard portfolio={portfolio} />;
}
