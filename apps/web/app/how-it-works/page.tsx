import Image from "next/image";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const steps = [
  ["Add a source", "Start with a public wallet address or an exchange statement you exported."],
  ["Review the records", "PocketOrbit checks the file, lines up asset identities, and marks records that need attention."],
  ["See one portfolio", "Balances and supported activity are grouped into a portfolio view using repeatable calculations."],
  ["Trace the details", "Open source details to see where a balance or price came from and when it was retrieved."]
];

export default function HowItWorksPage() {
  return (
    <>
      <SiteHeader />
      <main className="page-container section-space detail-page">
        <section className="feature-intro">
          <div>
            <span className="badge badge--violet">How it works</span>
            <h1 className="page-title">From scattered records to a clearer picture.</h1>
            <p className="body-copy">PocketOrbit is designed to organize supported records and keep their source information attached. It never needs permission to move your crypto.</p>
          </div>
          <aside className="feature-mascot-card">
            <Image src="/brand/pocketorbit-comet.png" alt="" aria-hidden="true" width={330} height={347} />
            <p><strong>Follow the activity.</strong><span>Each step adds context, so the summary is easier to make sense of.</span></p>
          </aside>
        </section>

        <section className="process-grid" aria-label="How PocketOrbit works">
          {steps.map(([title, body], index) => (
            <article className="process-step" key={title}>
              <span className="step-number">0{index + 1}</span>
              <h2>{title}</h2>
              <p>{body}</p>
            </article>
          ))}
        </section>

        <div className="read-only-panel">
          <span className="read-only-dot" />
          <div><strong>Always read-only</strong><p>Never provide a seed phrase or private key. Use public addresses or records you choose to import.</p></div>
          <Link className="text-link" href="/security">Read about security</Link>
        </div>
        <div className="detail-cta"><Link className="button button--primary" href="/app">Explore the sample portfolio</Link></div>
      </main>
      <SiteFooter />
    </>
  );
}
