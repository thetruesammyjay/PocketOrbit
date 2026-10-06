import Image from "next/image";
import Link from "next/link";

import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const principles = [
  {
    title: "See where a number came from",
    description: "A portfolio is easier to trust when you can check the source and when its information was gathered.",
    mark: "violet"
  },
  {
    title: "Know when information needs a closer look",
    description: "Missing, old, or conflicting records should be called out clearly, not smoothed over.",
    mark: "sun"
  },
  {
    title: "Bring different records together",
    description: "PocketOrbit is designed to organize public wallet records and exchange files in one view.",
    mark: "sky"
  }
];

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main>
        <section className="page-container landing-hero">
          <div className="landing-copy-block">
            <span className="badge badge--violet">A calmer way to see your crypto</span>
            <h1 className="landing-title">Your crypto, in one clear view.</h1>
            <p className="landing-copy">
              Bring public wallets and exchange statements together. See what you own, where it is held, and how each number was gathered.
            </p>
            <div className="landing-actions">
              <Link className="button button--primary" href="/app">Explore the sample portfolio</Link>
              <Link className="button button--secondary" href="/how-it-works">How it works</Link>
            </div>
            <ul className="trust-points" aria-label="PocketOrbit principles">
              <li><i className="trust-mark trust-mark--mint" />Read-only by design</li>
              <li><i className="trust-mark trust-mark--violet" />No private keys</li>
              <li><i className="trust-mark trust-mark--sky" />Sources matter</li>
            </ul>
          </div>
          <div className="hero-visual-wrap">
            <div className="hero-visual-label"><span className="orbit-indicator" />One portfolio, more context</div>
            <div className="hero-visual">
              <Image
                src="/brand/PocketOrbit-Product-Flow.png"
                alt="Add a public wallet or exchange file, organize records, see your portfolio, and check the details behind it."
                width={1536}
                height={1024}
                priority
              />
            </div>
            <div className="mascot-caption">
              <Image src="/brand/PocketOrbit-Orbit.png" alt="" aria-hidden="true" width={1112} height={971} />
              <span><strong>Clarity, from source to summary.</strong><small>The demo uses illustrative sample values.</small></span>
            </div>
          </div>
        </section>

        <section className="page-container section-space landing-context">
          <div className="section-intro">
            <div>
              <span className="eyebrow">A portfolio with context</span>
              <h2 className="section-title">A number is more useful when you can see what it means.</h2>
            </div>
            <p className="body-copy">
              PocketOrbit is being built to make scattered records easier to understand, with sources, timestamps, and data quality kept in view.
            </p>
          </div>
          <div className="principles-grid">
            {principles.map((principle) => (
              <article className="principle" key={principle.title}>
                <span className={`principle-mark principle-mark--${principle.mark}`} aria-hidden="true" />
                <h3>{principle.title}</h3>
                <p>{principle.description}</p>
              </article>
            ))}
          </div>
        </section>

        <section className="page-container landing-demo-wrap">
          <div className="landing-demo">
            <div>
              <span className="eyebrow">Take a look around</span>
              <h2 className="section-title">See how a clearer portfolio feels.</h2>
              <p>The sample portfolio is ready to explore. No wallet connection is needed.</p>
            </div>
            <Link className="button button--primary" href="/app">Open the sample portfolio</Link>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
