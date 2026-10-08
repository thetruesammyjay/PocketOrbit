import { PageHeading } from "@/components/page-heading";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";
import { formatCurrency } from "@/lib/format";

export default async function InsightsPage() {
  const portfolio = await getPortfolioSummary();
  const pricedHoldings = portfolio.holdings.filter((holding) => holding.value !== null);
  const topHolding = [...pricedHoldings].sort((left, right) => Number(right.value) - Number(left.value))[0];
  const knownValue = Number(portfolio.knownValue);
  const topShare = topHolding && knownValue > 0
    ? (Number(topHolding.value) / knownValue) * 100
    : null;
  const walletCount = portfolio.sources.filter((source) => source.kind === "wallet").length;
  const importedSourceCount = portfolio.sources.filter((source) => source.kind.startsWith("exchange_")).length;
  const change = portfolio.change24h === null ? null : Number(portfolio.change24h);

  return <><PageHeading title="Insights" description={portfolio.isDemo ? "Plain-language notes about the sample portfolio." : "Plain-language notes based on saved portfolio data."} />{portfolio.isDemo && <div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Illustrative insights</strong>These observations use sample values, not live holdings.</div></div>}<div className="content-grid"><article className="panel content-panel"><span className="eyebrow">Largest priced holding</span><h2 style={{ marginTop: "0.55rem" }}>{topHolding ? topHolding.asset.name : "No priced holdings yet"}</h2><p>{topHolding && topShare !== null ? `${topShare.toFixed(1)}% of the known priced subtotal, worth ${formatCurrency(topHolding.value, portfolio.reportingCurrency)}.` : "A position appears here after a saved balance has a recognized price."}</p></article><article className="panel content-panel"><span className="eyebrow">Connected sources</span><h2 style={{ marginTop: "0.55rem" }}>{walletCount} {walletCount === 1 ? "wallet" : "wallets"} · {importedSourceCount} {importedSourceCount === 1 ? "import" : "imports"}</h2><p>{portfolio.sources.length ? "Each saved source keeps its own update time and data quality." : "Add a public wallet or import a current balance statement to begin."}</p></article><article className="panel content-panel"><span className="eyebrow">Data quality</span><h2 style={{ marginTop: "0.55rem" }}>{portfolio.quality.replaceAll("_", " ")}</h2><p>{portfolio.totalValue === null ? "The portfolio total is withheld while source coverage, prices, or review items are incomplete." : "The portfolio total includes the saved balances and recognized prices currently available."}</p>{portfolio.warnings.length > 0 && <ul>{portfolio.warnings.slice(0, 3).map((warning) => <li key={warning}>{warning}</li>)}</ul>}</article><article className="panel content-panel"><span className="eyebrow">24-hour context</span><h2 style={{ marginTop: "0.55rem" }}>{change === null ? "Not enough saved history" : `${change >= 0 ? "+" : ""}${formatCurrency(change, portfolio.reportingCurrency)}`}</h2><p>{portfolio.changePercent24h === null ? "A comparison appears after complete portfolio values span at least 24 hours." : `${Number(portfolio.changePercent24h) >= 0 ? "+" : ""}${Number(portfolio.changePercent24h).toFixed(2)}% from the saved portfolio value 24 hours earlier.`}</p></article></div></>;
}
