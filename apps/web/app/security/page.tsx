import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const principles = [
  ["Never share", "PocketOrbit will not ask for seed phrases, private keys, recovery words, or wallet signing access."],
  ["No asset controls", "The product does not custody assets or execute trades, transfers, swaps, bridges, or withdrawals."],
  ["Visible data sources", "Balances and prices are intended to show their source and retrieval time. Partial or stale information should be labeled."],
  ["Know what is ready", "Authentication, storage, and provider security controls are not configured in this starter yet."]
];

export default function SecurityPage() {
  return (
    <>
      <SiteHeader />
      <main className="page-container section-space detail-page">
        <section className="feature-intro feature-intro--plain">
          <div>
            <span className="badge badge--success">Read-only by design</span>
            <h1 className="page-title">Your keys stay with you.</h1>
            <p className="body-copy">PocketOrbit is a portfolio companion, not a wallet. It is designed around public addresses and files you choose to import.</p>
          </div>
          <div className="security-orbit" aria-hidden="true"><span /><span /><span /></div>
        </section>

        <div className="content-grid security-grid">
          {principles.map(([title, body]) => (
            <section className="panel content-panel" key={title}>
              <span className="security-mark" aria-hidden="true" />
              <h2>{title}</h2>
              <p>{body}</p>
            </section>
          ))}
        </div>

        <div className="detail-note"><strong>This is an early scaffold.</strong><p>Live connections and account features are not configured. The sample portfolio uses illustrative values only.</p><Link className="text-link" href="/app">Explore the sample portfolio</Link></div>
      </main>
      <SiteFooter />
    </>
  );
}
