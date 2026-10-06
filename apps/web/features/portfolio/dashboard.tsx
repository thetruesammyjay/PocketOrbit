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
  return (
    <>
      <div className="dashboard-heading">
        <div>
          <h1 className="page-title">Your portfolio</h1>
          <p>One view of the assets in this sample portfolio.</p>
        </div>
        <Badge tone="warning">Sample values</Badge>
      </div>

      <div className="demo-banner" role="note">
        <span aria-hidden="true">i</span>
        <div><strong>This is a sample portfolio</strong>These values are illustrative. No wallet or exchange account is connected, and nothing here reflects live market prices.</div>
      </div>

      <div className="metric-grid" aria-label="Sample portfolio summary">
        <Card className="metric-card"><div className="metric-label">Total value · USD</div><div className="metric-value tabular">{formatCurrency(portfolio.totalValue)}</div><div className="metric-detail">Sample calculation</div></Card>
        <Card className="metric-card"><div className="metric-label">24-hour change</div><div className="metric-value tabular">+{formatCurrency(portfolio.change24h)}</div><div className="metric-detail">{formatPercent(portfolio.changePercent24h, true)} · illustrative</div></Card>
        <Card className="metric-card"><div className="metric-label">Assets</div><div className="metric-value tabular">{portfolio.holdings.length}</div><div className="metric-detail">Across sample sources</div></Card>
        <Card className="metric-card"><div className="metric-label">Sources</div><div className="metric-value tabular">{portfolio.sources.length}</div><div className="metric-detail">Wallets and one sample file</div></Card>
      </div>

      <div className="dashboard-main-grid">
        <div className="dashboard-stack">
          <Card className="value-card">
            <div className="panel-heading"><div><h2>Portfolio value</h2><p>Illustrative history · sample data</p></div><QualityStatusBadge status={portfolio.quality} /></div>
            <div className="value-main"><div className="total-value tabular">{formatCurrency(portfolio.totalValue)}</div><div className="value-change">+{formatCurrency(portfolio.change24h)} <small>({formatPercent(portfolio.changePercent24h, true)}) in sample data</small></div></div>
            <div className="chart-wrap"><PortfolioChart values={portfolio.history} /></div>
            <div className="range-row" aria-label="Chart time ranges">
              <span className="range-chip" aria-current="true">Seven-day sample window</span>
            </div>
          </Card>
          <Card>
            <div className="panel-heading"><div><h2>Assets</h2><p>Balances grouped by asset</p></div><Link className="text-link muted" href="/app/portfolio">View portfolio</Link></div>
            <div className="table-wrap">
              <table className="data-table">
                <thead><tr><th>Asset</th><th>Quantity</th><th className="numeric">Value</th></tr></thead>
                <tbody>{portfolio.holdings.slice(0, 4).map((holding) => <tr key={holding.asset.id}><td><div className="asset-cell"><span className="asset-dot">{holding.asset.symbol.slice(0, 3)}</span><span className="asset-name"><strong>{holding.asset.name}</strong><span>{holding.asset.symbol}</span></span></div></td><td className="tabular">{holding.quantity}</td><td className="numeric"><strong>{formatCurrency(holding.value)}</strong></td></tr>)}</tbody>
              </table>
            </div>
          </Card>
          <Card>
            <div className="panel-heading"><div><h2>Recent activity</h2><p>Sample records from different sources</p></div><Link className="text-link muted" href="/app/activity">See activity</Link></div>
            <ActivityList items={portfolio.activity.slice(0, 3)} />
          </Card>
        </div>

        <div className="dashboard-stack">
          <AllocationBreakdown items={portfolio.allocation} />
          <Card>
            <div className="panel-heading"><div><h2>Accounts and wallets</h2><p>Where sample assets are held</p></div></div>
            <div className="source-list">{portfolio.sources.map((source) => <div className="source-row" key={source.id}><span className="source-symbol">{sourceMark(source.kind)}</span><span className="source-copy"><strong>{source.name}</strong><span>{source.network ?? source.addressLabel ?? "Imported record"}</span></span><QualityStatusBadge status={source.quality} /></div>)}</div>
          </Card>
          <Card className="quality-card">
            <div className="panel-heading" style={{ padding: "0 0 0.5rem" }}><div><h2>Data quality</h2><p>Limits that affect this view</p></div></div>
            <div className="quality-row"><span>Balance source</span><strong>Sample records</strong></div>
            <div className="quality-row"><span>Price source</span><strong>Illustrative prices</strong></div>
            <div className="quality-row"><span>Last updated</span><strong>Demo snapshot</strong></div>
            <div className="quality-row"><span>Live connection</span><strong>No</strong></div>
          </Card>
        </div>
      </div>
    </>
  );
}
