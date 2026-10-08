import Link from "next/link";
import { Badge, Card } from "@pocketorbit/ui";

import { ActivityList } from "@/features/activity/activity-list";
import { AllocationBreakdown } from "@/features/portfolio/allocation-breakdown";
import { PortfolioChart } from "@/features/portfolio/portfolio-chart";
import { QualityStatusBadge } from "@/components/quality-status";
import { formatCurrency, formatPercent } from "@/lib/format";
import type { PortfolioSummary } from "@pocketorbit/types";

function sourceMark(kind: string) {
  return kind === "wallet" ? "W" : "CSV";
}

export function Dashboard({ portfolio }: { portfolio: PortfolioSummary }) {
  const isDemo = portfolio.isDemo;
  const hasBalanceSnapshot = portfolio.sources.some(
    (source) => (source.kind === "wallet" || source.kind === "exchange_balance_import") && Boolean(source.lastUpdatedAt)
  );
  const displayedTotal = portfolio.totalValue === null
    ? hasBalanceSnapshot
      ? formatCurrency(portfolio.knownValue, portfolio.reportingCurrency)
      : "—"
    : formatCurrency(portfolio.totalValue, portfolio.reportingCurrency);
  const lastUpdated = portfolio.sources
    .map((source) => source.lastUpdatedAt)
    .filter((value): value is string => Boolean(value))
    .sort()
    .at(-1);

  return (
    <>
      <div className="dashboard-heading">
        <div>
          <h1 className="page-title">{portfolio.name}</h1>
          <p>{isDemo ? "A sample portfolio, clearly labeled." : "One view of the assets in your connected sources."}</p>
        </div>
        {isDemo ? <Badge tone="warning">Sample values</Badge> : <QualityStatusBadge status={portfolio.quality} />}
      </div>

      {isDemo && <div className="demo-banner" role="note"><span aria-hidden="true">i</span><div><strong>This is a sample portfolio</strong>These values are illustrative. No wallet or exchange account is connected, and nothing here reflects live market prices.</div></div>}
      {portfolio.warnings.map((warning) => <div className="data-warning-note" role="note" key={warning}>{warning}</div>)}

      <div className="metric-grid" aria-label="Portfolio summary">
        <Card className="metric-card"><div className="metric-label">{portfolio.totalValue === null && hasBalanceSnapshot ? `Known value · ${portfolio.reportingCurrency}` : `Portfolio value · ${portfolio.reportingCurrency}`}</div><div className="metric-value tabular">{displayedTotal}</div><div className="metric-detail">{!hasBalanceSnapshot && !isDemo ? "Connect a public wallet or import current exchange balances" : portfolio.totalValue === null ? "Some balances or prices need review" : isDemo ? "Sample calculation" : portfolio.quality.replaceAll("_", " ")}</div></Card>
        <Card className="metric-card"><div className="metric-label">24-hour change</div><div className="metric-value tabular">{portfolio.change24h === null ? "—" : `${Number(portfolio.change24h) >= 0 ? "+" : ""}${formatCurrency(portfolio.change24h, portfolio.reportingCurrency)}`}</div><div className="metric-detail">{portfolio.changePercent24h === null ? "Available after enough snapshots" : `${formatPercent(portfolio.changePercent24h, true)}${isDemo ? " · illustrative" : ""}`}</div></Card>
        <Card className="metric-card"><div className="metric-label">Assets</div><div className="metric-value tabular">{portfolio.holdings.length}</div><div className="metric-detail">{isDemo ? "Across sample sources" : "Recognized positions"}</div></Card>
        <Card className="metric-card"><div className="metric-label">Sources</div><div className="metric-value tabular">{portfolio.sources.length}</div><div className="metric-detail">{isDemo ? "Sample wallets and file" : "Wallets and imported records"}</div></Card>
      </div>

      <div className="dashboard-main-grid">
        <div className="dashboard-stack">
          <Card className="value-card">
            <div className="panel-heading"><div><h2>Portfolio value</h2><p>{isDemo ? "Illustrative sample history" : "Saved portfolio snapshots"}</p></div><QualityStatusBadge status={portfolio.quality} /></div>
            <div className="value-main"><div className="total-value tabular">{displayedTotal}</div><div className="value-change">{portfolio.change24h === null ? <small>Change appears after a full day of saved snapshots.</small> : <>{Number(portfolio.change24h) >= 0 ? "+" : ""}{formatCurrency(portfolio.change24h, portfolio.reportingCurrency)} <small>({formatPercent(portfolio.changePercent24h ?? "0", true)}) over 24 hours</small></>}</div></div>
            <div className="chart-wrap">{portfolio.history.length >= 2 ? <PortfolioChart values={portfolio.history} sample={isDemo} /> : <p className="empty-chart-note">Your chart will fill in as PocketOrbit saves more portfolio snapshots.</p>}</div>
            {portfolio.history.length >= 2 && <div className="range-row" aria-label="Chart time range"><span className="range-chip" aria-current="true">Saved history</span></div>}
          </Card>

          <Card>
            <div className="panel-heading"><div><h2>Assets</h2><p>Balances grouped by asset</p></div><Link className="text-link muted" href="/app/portfolio">View portfolio</Link></div>
            <div className="table-wrap">
              {portfolio.holdings.length > 0 ? <table className="data-table">
                <thead><tr><th>Asset</th><th>Quantity</th><th className="numeric">Value</th></tr></thead>
                <tbody>{portfolio.holdings.slice(0, 4).map((holding) => <tr key={holding.asset.id}><td><div className="asset-cell"><span className="asset-dot">{holding.asset.symbol.slice(0, 3)}</span><span className="asset-name"><strong>{holding.asset.name}</strong><span>{holding.asset.symbol}</span></span></div></td><td className="tabular">{holding.quantity}</td><td className="numeric"><strong>{holding.value === null ? "Unpriced" : formatCurrency(holding.value, portfolio.reportingCurrency)}</strong></td></tr>)}</tbody>
              </table> : <p className="empty-panel-copy">Connect a public wallet or import a current balance statement to add holdings here. Transaction history appears under Activity.</p>}
            </div>
          </Card>

          <Card>
            <div className="panel-heading"><div><h2>Recent activity</h2><p>{isDemo ? "Sample records from different sources" : "Imported transaction records"}</p></div><Link className="text-link muted" href="/app/activity">See activity</Link></div>
            {portfolio.activity.length ? <ActivityList items={portfolio.activity.slice(0, 3)} /> : <p className="empty-panel-copy">Imported transaction history will appear here.</p>}
          </Card>
        </div>

        <div className="dashboard-stack">
          <AllocationBreakdown items={portfolio.allocation} currency={portfolio.reportingCurrency} sample={isDemo} />
          <Card>
            <div className="panel-heading"><div><h2>Accounts and wallets</h2><p>{isDemo ? "Sample source locations" : "Where recognized assets are held"}</p></div></div>
            <div className="source-list">{portfolio.sources.map((source) => <div className="source-row" key={source.id}><span className="source-symbol">{sourceMark(source.kind)}</span><span className="source-copy"><strong>{source.name}</strong><span>{source.network ?? source.addressLabel ?? "Imported record"}</span></span><QualityStatusBadge status={source.quality} /></div>)}{portfolio.sources.length === 0 && <p className="empty-panel-copy">No sources yet. Add a wallet or import a file to start.</p>}</div>
          </Card>
          <Card className="quality-card">
            <div className="panel-heading" style={{ padding: "0 0 0.5rem" }}><div><h2>Data quality</h2><p>Limits that affect this view</p></div></div>
            <div className="quality-row"><span>Balance source</span><strong>{isDemo ? "Sample records" : "Shown per asset"}</strong></div>
            <div className="quality-row"><span>Price source</span><strong>{isDemo ? "Illustrative prices" : "Shown per asset"}</strong></div>
            <div className="quality-row"><span>Last updated</span><strong>{isDemo ? "Demo snapshot" : lastUpdated ? new Date(lastUpdated).toLocaleString() : "No sync yet"}</strong></div>
            <div className="quality-row"><span>Connection</span><strong>{isDemo ? "Sample only" : "Read-only"}</strong></div>
          </Card>
        </div>
      </div>
    </>
  );
}
