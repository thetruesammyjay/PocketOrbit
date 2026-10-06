import { PageHeading } from "@/components/page-heading";
import { QualityStatusBadge } from "@/components/quality-status";
import { HoldingsTable } from "@/features/portfolio/holdings-table";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function PortfolioPage() {
  const portfolio = await getPortfolioSummary();
  return <><PageHeading title="Portfolio" description="Sample holdings grouped by asset." action={<QualityStatusBadge status={portfolio.quality} />} /><div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Illustrative sample data</strong>These balances and prices are not live and are not connected to an account.</div></div><HoldingsTable holdings={portfolio.holdings} currency={portfolio.reportingCurrency} /></>;
}
