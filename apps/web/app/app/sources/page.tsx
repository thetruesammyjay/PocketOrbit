import Image from "next/image";
import Link from "next/link";

import { PageHeading } from "@/components/page-heading";
import { QualityStatusBadge } from "@/components/quality-status";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";
import { WalletSourceActions } from "@/features/wallets/wallet-source-actions";

export default async function SourcesPage() {
  const portfolio = await getPortfolioSummary();

  return (
    <>
      <PageHeading
        title="Sources"
        description={portfolio.isDemo ? "Examples of where portfolio records can come from." : "Wallets and files contributing to this portfolio."}
        action={<Link className="button button--secondary" href="/app/wallets/add">Add a wallet</Link>}
      />
      {portfolio.isDemo && <div className="demo-banner"><span aria-hidden="true">i</span><div><strong>No sources are connected</strong>The items below are examples to show how source details will appear.</div></div>}
      {!portfolio.sources.length && !portfolio.isDemo ? <section className="panel content-panel"><h2>No sources yet</h2><p>Add a public wallet or import an exchange file to start.</p><Link className="button button--primary" href="/app/wallets/add">Add a wallet</Link></section> : <>
        <aside className="app-mascot-note">
          <Image src="/brand/pocketorbit-scout.png" alt="" aria-hidden="true" width={284} height={362} />
          <p><strong>Keep the source in sight.</strong><span>Each source has its own update time and data quality. Review those details before relying on a total.</span></p>
        </aside>
        <div className="content-grid">
          {portfolio.sources.map((source) => (
            <article className="panel content-panel" key={source.id}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem" }}>
                <h2>{source.name}</h2>
                <QualityStatusBadge status={source.quality} />
              </div>
              <p>{source.kind === "wallet" ? `Public wallet · ${source.network}` : source.kind === "exchange_balance_import" ? "Exchange balance statement" : source.kind === "exchange_import" ? "Exchange transaction file" : "Connected exchange"}</p>
              <hr className="divider" style={{ margin: "1rem 0" }} />
              <p><strong>Address:</strong> {source.addressLabel ?? "Not applicable"}</p>
              <p><strong>Last sync:</strong> {source.lastUpdatedAt ? new Date(source.lastUpdatedAt).toLocaleString() : "Not synced yet"}</p>
              {source.coverage && <p><strong>Coverage:</strong> {source.coverage.replaceAll("_", " ")}</p>}
              <p><strong>Assets:</strong> {portfolio.holdings.filter((holding) => holding.sourceIds.includes(source.id)).map((holding) => holding.asset.symbol).join(", ") || "None recognized"}</p>
              {source.warnings?.map((warning) => <p className="source-warning" key={warning}>{warning}</p>)}
              {source.kind === "wallet" && <WalletSourceActions portfolioId={portfolio.id} sourceId={source.id} sourceName={source.name} />}
            </article>
          ))}
        </div>
      </>}
    </>
  );
}
