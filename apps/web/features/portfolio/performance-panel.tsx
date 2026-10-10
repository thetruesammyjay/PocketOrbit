"use client";

import { useEffect, useState } from "react";

import { API_BASE_PATH } from "@/lib/api-base-path";
import { formatCurrency } from "@/lib/format";

type Performance = {
  status: "complete" | "partial" | "unavailable";
  method: string;
  currency: string;
  realizedPnl: string | null;
  unrealizedPnl: string | null;
  totalPnl: string | null;
  openPositions: { assetSymbol: string; quantity: string; costBasis: string | null; marketValue: string | null; pnl: string | null; sourceNames: string[] }[];
  realizedEvents: { transactionId: string; assetSymbol: string; sourceName: string; quantity: string; proceeds: string | null; costBasis: string | null; pnl: string | null; method: string }[];
  coverage: { sourceName: string; startAt: string | null; endAt: string | null; completeHistoryAsserted: boolean; rowsImported: number; rowsRejected: number }[];
  reasons: string[];
  calculatedAt: string;
};

export function PerformancePanel({ portfolioId }: { portfolioId: string }) {
  const [performance, setPerformance] = useState<Performance | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;
    void fetch(`${API_BASE_PATH}/portfolios/${encodeURIComponent(portfolioId)}/performance`, {
      credentials: "include",
      cache: "no-store"
    }).then(async (response) => {
      const payload = await response.json();
      if (!response.ok) throw new Error(typeof payload.detail === "string" ? payload.detail : "Performance could not be loaded.");
      if (active) setPerformance(payload as Performance);
    }).catch((cause: unknown) => {
      if (active) setError(cause instanceof Error ? cause.message : "Performance could not be loaded.");
    });
    return () => { active = false; };
  }, [portfolioId]);

  if (error) return <section className="panel content-panel"><h2>Performance is unavailable</h2><p>{error}</p></section>;
  if (!performance) return <section className="panel content-panel"><p>Calculating FIFO performance…</p></section>;
  const statusLabel = performance.status === "complete" ? "Complete for the stated history" : performance.status === "partial" ? "Partial · review the gaps" : "Unavailable";

  return <div className="performance-stack">
    <section className="panel content-panel">
      <div className="panel-heading"><div><h2>Performance · {performance.method}</h2><p>Cost basis uses FIFO and imported transaction values in {performance.currency}. This is a portfolio calculation, not tax advice.</p></div><span className={`performance-status performance-status--${performance.status}`}>{statusLabel}</span></div>
      <div className="metric-grid performance-metrics">
        <div className="metric-card"><div className="metric-label">Realized P&amp;L · known records</div><div className="metric-value tabular">{performance.realizedPnl === null ? "—" : formatCurrency(performance.realizedPnl, performance.currency)}</div></div>
        <div className="metric-card"><div className="metric-label">Unrealized P&amp;L · known lots</div><div className="metric-value tabular">{performance.unrealizedPnl === null ? "—" : formatCurrency(performance.unrealizedPnl, performance.currency)}</div></div>
        <div className="metric-card"><div className="metric-label">Total P&amp;L</div><div className="metric-value tabular">{performance.totalPnl === null ? "Not available" : formatCurrency(performance.totalPnl, performance.currency)}</div><div className="metric-detail">A total appears only when the reviewed data has no known gaps.</div></div>
      </div>
      {performance.reasons.length > 0 && <div className="data-warning-note"><strong>What is incomplete</strong><ul>{performance.reasons.map((reason) => <li key={reason}>{reason}</li>)}</ul></div>}
    </section>

    <section className="panel content-panel"><div className="panel-heading"><div><h2>Transaction history coverage</h2><p>Dates show the earliest and latest records observed in each imported account.</p></div></div>{performance.coverage.length ? <div className="import-history">{performance.coverage.map((item) => <div className="import-history-row" key={item.sourceName}><span><strong>{item.sourceName}</strong><small>{item.startAt ? `${new Date(item.startAt).toLocaleDateString()} – ${new Date(item.endAt ?? item.startAt).toLocaleDateString()}` : "No dated records"} · {item.rowsImported} imported · {item.rowsRejected} rejected · {item.completeHistoryAsserted ? "full history asserted" : "partial history"}</small></span></div>)}</div> : <p className="empty-panel-copy">No exchange transaction exports have been imported.</p>}</section>

    {performance.openPositions.length > 0 && <section className="panel content-panel"><div className="panel-heading"><div><h2>Open FIFO lots</h2><p>Older acquisitions are consumed first. Missing basis or prices remain blank.</p></div></div><div className="table-wrap"><table className="data-table"><thead><tr><th>Asset</th><th>Quantity</th><th>Cost basis</th><th>Market value</th><th>Unrealized P&amp;L</th></tr></thead><tbody>{performance.openPositions.map((position) => <tr key={`${position.assetSymbol}-${position.sourceNames.join("-")}`}><td><strong>{position.assetSymbol}</strong><small className="table-subcopy">{position.sourceNames.join(", ")}</small></td><td>{position.quantity}</td><td>{position.costBasis === null ? "Unknown" : formatCurrency(position.costBasis, performance.currency)}</td><td>{position.marketValue === null ? "Unpriced" : formatCurrency(position.marketValue, performance.currency)}</td><td>{position.pnl === null ? "Unavailable" : formatCurrency(position.pnl, performance.currency)}</td></tr>)}</tbody></table></div></section>}

    {performance.realizedEvents.length > 0 && <section className="panel content-panel"><div className="panel-heading"><div><h2>Realized events</h2><p>Each sale shows its imported proceeds and FIFO basis.</p></div></div><div className="table-wrap"><table className="data-table"><thead><tr><th>Asset</th><th>Account</th><th>Quantity</th><th>Proceeds</th><th>FIFO basis</th><th>Known P&amp;L</th></tr></thead><tbody>{performance.realizedEvents.map((event) => <tr key={event.transactionId}><td>{event.assetSymbol}</td><td>{event.sourceName}</td><td>{event.quantity}</td><td>{event.proceeds === null ? "Unknown" : formatCurrency(event.proceeds, performance.currency)}</td><td>{event.costBasis === null ? "Unknown" : formatCurrency(event.costBasis, performance.currency)}</td><td>{event.pnl === null ? "Unavailable" : formatCurrency(event.pnl, performance.currency)}</td></tr>)}</tbody></table></div></section>}
  </div>;
}
