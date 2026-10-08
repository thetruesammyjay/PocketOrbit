import { PageHeading } from "@/components/page-heading";
import { QualityStatusBadge } from "@/components/quality-status";
import { HoldingsTable } from "@/features/portfolio/holdings-table";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function PortfolioPage() {
  const portfolio = await getPortfolioSummary();
  return <><PageHeading title="Portfolio" description={portfolio.isDemo ? "Sample holdings grouped by asset." : "Holdings with their balance and price sources."} action={<QualityStatusBadge status={portfolio.quality} />} />{portfolio.isDemo && <div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Illustrative sample data</strong>These balances and prices are not live and are not connected to an account.</div></div>}{portfolio.holdings.length ? <HoldingsTable holdings={portfolio.holdings} currency={portfolio.reportingCurrency} /> : <section className="panel content-panel"><h2>No holdings yet</h2><p>Connect a public wallet or import a current balance statement. Transaction history appears under Activity.</p></section>}</>;
}
