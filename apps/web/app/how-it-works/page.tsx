import Image from "next/image";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const steps = [
  ["Add a source", "Start with a public wallet address or an exchange statement you exported."],
  ["Review the records", "The planned workflow lines up assets and marks records that need attention."],
  ["See one portfolio", "Supported balances and activity are intended to come together in one understandable view."],
  ["Trace the details", "Check where a balance or price came from and when its information was gathered."]
];

export default function HowItWorksPage() {
  return (
    <>
      <SiteHeader />
      <main className="page-container section-space detail-page">
        <section className="marketing-subpage-hero">
          <div className="marketing-subpage-copy">
            <span className="badge badge--violet">How it works</span>
            <h1 className="page-title">A clearer path from records to portfolio.</h1>
            <p className="body-copy">PocketOrbit is designed to bring supported records together and keep the source attached to every useful detail. It does not need permission to move your assets.</p>
            <Link className="button button--primary" href="/app">Explore the sample portfolio</Link>
          </div>
          <div className="marketing-subpage-art marketing-subpage-art--sources">
            <Image src="/illustrations/source-assembly.svg" alt="Public wallet and exchange file joining one portfolio view" width={560} height={350} priority />
            <Image className="marketing-subpage-mascot" src="/brand/pocketorbit-comet.png" alt="" aria-hidden="true" width={330} height={347} />
          </div>
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

        <figure className="marketing-flow-figure">
          <Image src="/brand/PocketOrbit-Product-Flow.png" alt="The four-part PocketOrbit concept: add a source, organize records, see the portfolio, and check the details." width={1536} height={1024} />
          <figcaption>This diagram shows the intended workflow. The current portfolio demo contains illustrative sample values.</figcaption>
        </figure>

        <div className="read-only-panel">
          <span className="read-only-dot" />
          <div><strong>Always read-only</strong><p>Never provide a seed phrase or private key. Use public addresses or records you choose to import.</p></div>
          <Link className="text-link" href="/security">Read about security</Link>
        </div>
      </main>
      <SiteFooter />
    </>
  );
}
