import { PageHeading } from "@/components/page-heading";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";
import { API_BASE_PATH } from "@/lib/api-base-path";

export default async function ReportsPage() {
  const portfolio = await getPortfolioSummary();
  if (portfolio.isDemo) {
    return <><PageHeading title="Reports" description="Download an example holdings file." /><section className="panel content-panel"><h2>Sample holdings CSV</h2><p>This file contains illustrative values. It is not an account statement.</p><a className="button button--secondary" href={`${API_BASE_PATH}/reports/demo/holdings.csv`}>Download sample CSV</a></section></>;
  }

  return <><PageHeading title="Reports" description="Export the latest saved holdings in this portfolio." /><section className="panel content-panel"><h2>{portfolio.name} holdings</h2><p>The CSV includes quantities, prices, values, data quality, sources, and update times. Missing prices stay blank; incomplete portfolio totals are not presented as complete.</p><a className="button button--secondary" href={`${API_BASE_PATH}/reports/portfolios/${encodeURIComponent(portfolio.id)}/holdings.csv`}>Download holdings CSV</a></section></>;
}
