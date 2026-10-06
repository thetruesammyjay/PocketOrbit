import Image from "next/image";
import Link from "next/link";

import { PageHeading } from "@/components/page-heading";
import { QualityStatusBadge } from "@/components/quality-status";
import { getPortfolioSummary } from "@/features/portfolio/portfolio-api";

export default async function SourcesPage() {
  const portfolio = await getPortfolioSummary();

  return (
    <>
      <PageHeading
        title="Sources"
        description="See which wallets and records contribute to this sample."
        action={<Link className="button button--secondary" href="/app/wallets/add">Add a wallet</Link>}
      />
      <div className="demo-banner">
        <span aria-hidden="true">i</span>
        <div><strong>No sources are connected</strong>The items below are examples to show how source details will appear.</div>
      </div>
      <aside className="app-mascot-note">
        <Image src="/brand/pocketorbit-scout.png" alt="" aria-hidden="true" width={284} height={362} />
        <p><strong>Keep the source in sight.</strong><span>Wallets and imported files can each tell a different part of the story. These examples are not live connections.</span></p>
      </aside>
      <div className="content-grid">
        {portfolio.sources.map((source) => (
          <article className="panel content-panel" key={source.id}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", gap: "0.5rem" }}>
              <h2>{source.name}</h2>
              <QualityStatusBadge status={source.quality} />
            </div>
            <p>{source.kind === "wallet" ? `Public wallet · ${source.network}` : "Exchange statement · sample CSV"}</p>
            <hr className="divider" style={{ margin: "1rem 0" }} />
            <p><strong>Reference:</strong> {source.addressLabel}</p>
            <p><strong>Freshness:</strong> Sample snapshot</p>
            <p><strong>Assets:</strong> {portfolio.holdings.filter((holding) => holding.sourceIds.includes(source.id)).map((holding) => holding.asset.symbol).join(", ") || "None"}</p>
          </article>
        ))}
      </div>
    </>
  );
}
