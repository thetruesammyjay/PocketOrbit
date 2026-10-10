import Image from "next/image";
import Link from "next/link";

import { CryptoAssetIcon } from "@/components/crypto-asset-icon";
import { PortfolioPreview } from "@/components/portfolio-preview";
import { ScrollReveal } from "@/components/scroll-reveal";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const features = [
  {
    image: "/illustrations/source-assembly.svg",
    alt: "Public wallet and exchange file joining one portfolio view",
    title: "One portfolio, many places.",
    description: "PocketOrbit is designed to bring public wallets and exchange files into one understandable picture.",
    className: "marketing-feature-card--sources"
  },
  {
    image: "/illustrations/number-receipt.svg",
    alt: "Sample portfolio value with source, update, and quality details",
    title: "Know where a number came from.",
    description: "See the source, last update, and quality label behind the value you are looking at.",
    className: "marketing-feature-card--receipts"
  },
  {
    image: "/illustrations/read-only-orbit.svg",
    alt: "Read-only shield with public address and file symbols",
    title: "Your keys stay with you.",
    description: "Public addresses and files are enough for the planned view. PocketOrbit never needs a seed phrase or private key.",
    className: "marketing-feature-card--privacy"
  }
];

const heroAssets = [
  { symbol: "BTC", share: "31.4%" },
  { symbol: "ETH", share: "21.9%" },
  { symbol: "SOL", share: "20.1%" }
] as const;

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main className="marketing-home">
        <section className="marketing-hero">
          <div className="page-container marketing-hero-layout">
            <div className="marketing-hero-copy">
              <h1><span>Your crypto,</span><span>in one clear view.</span></h1>
              <p>Bring public wallets and exchange statements together. See what you own, where it is held, and where each number came from.</p>
              <div className="marketing-hero-actions">
                <Link className="button button--primary" href="/app">Explore the sample portfolio</Link>
                <Link className="button button--secondary" href="/how-it-works">See how it works</Link>
              </div>
              <ul className="marketing-hero-trust" aria-label="PocketOrbit principles">
                <li><span className="marketing-trust-mark marketing-trust-mark--mint" />No private keys</li>
                <li><span className="marketing-trust-mark marketing-trust-mark--violet" />Sources on every number</li>
              </ul>
              <span className="marketing-hero-note">No account or wallet connection needed to explore the sample.</span>
            </div>

            <div className="marketing-hero-stage" role="img" aria-label="Illustrative portfolio preview: sample value of 31,686 US dollars from a public wallet and exchange file, with example Bitcoin, Ethereum, and Solana holdings">
              <div className="marketing-hero-stage-glow" />
              <div className="marketing-hero-orbit marketing-hero-orbit--outer" />
              <div className="marketing-hero-orbit marketing-hero-orbit--inner" />
              <div className="marketing-hero-source marketing-hero-source--wallet">
                <span className="marketing-hero-source-mark marketing-hero-source-mark--mint" aria-hidden="true">✓</span>
                <span><strong>Public wallet</strong><small>Read-only access</small></span>
              </div>
              <div className="marketing-hero-source marketing-hero-source--file">
                <span className="marketing-hero-source-mark marketing-hero-source-mark--violet" aria-hidden="true">
                  <svg viewBox="0 0 20 20" focusable="false"><path d="M5 2.75h6l4 4v10.5H5z" /><path d="M11 2.75v4h4M7.5 10h5M7.5 13h5" /></svg>
                </span>
                <span><strong>Exchange file</strong><small>CSV import</small></span>
              </div>
              <article className="marketing-hero-balance">
                <div className="marketing-hero-balance-top">
                  <div><span className="marketing-hero-card-label">Sample portfolio</span><strong className="marketing-hero-balance-value">$31,686.37</strong></div>
                  <span className="marketing-hero-sample-badge">Illustrative</span>
                </div>
                <div className="marketing-hero-balance-context"><span>Across 3 sample sources</span><span>USD</span></div>
                <svg className="marketing-hero-chart" viewBox="0 0 460 94" preserveAspectRatio="none" aria-hidden="true">
                  <path d="M0 76H460M0 47H460M0 18H460" className="marketing-hero-chart-grid" />
                  <path d="M0 70 38 62 76 66 114 48 152 55 190 38 228 45 266 31 304 35 342 20 380 27 420 11 460 8" className="marketing-hero-chart-line" pathLength={1} />
                  <circle cx="460" cy="8" r="5" className="marketing-hero-chart-point" />
                </svg>
                <div className="marketing-hero-assets" aria-hidden="true">
                  {heroAssets.map((asset) => (
                    <span className="marketing-hero-asset" key={asset.symbol}>
                      <CryptoAssetIcon symbol={asset.symbol} />
                      <span><strong>{asset.symbol}</strong><small>{asset.share}</small></span>
                    </span>
                  ))}
                </div>
              </article>
              <Image className="marketing-hero-mascot" src="/brand/PocketOrbit-Orbit.png" alt="" aria-hidden="true" width={1112} height={971} priority />
              <span className="marketing-hero-stage-caption"><span aria-hidden="true" />A clearer picture, with the source in sight</span>
            </div>
          </div>
        </section>

        <section className="marketing-showcase" aria-labelledby="showcase-title">
          <div className="page-container">
            <ScrollReveal className="marketing-showcase-heading-story">
              <div className="marketing-section-heading">
                <div>
                  <span className="marketing-section-kicker">A portfolio with context</span>
                  <h2 id="showcase-title">Everything in orbit. Every detail in sight.</h2>
                </div>
                <p>A calm view of your holdings only helps when it also shows the source, freshness, and uncertainty behind the numbers.</p>
              </div>
            </ScrollReveal>
            <ScrollReveal className="marketing-preview-reveal">
              <PortfolioPreview />
            </ScrollReveal>
          </div>
        </section>

        <section className="page-container marketing-features" id="features" aria-labelledby="features-title">
          <ScrollReveal className="marketing-feature-heading-story">
            <div className="marketing-section-heading marketing-section-heading--stacked">
              <span className="marketing-section-kicker">What makes the view clearer</span>
              <h2 id="features-title">The small details make a big difference.</h2>
            </div>
          </ScrollReveal>
          <ScrollReveal className="marketing-feature-reveal">
            <div className="marketing-feature-grid">
              {features.map((feature) => (
                <article className={`marketing-feature-card ${feature.className}`} key={feature.title}>
                  <div className="marketing-feature-art">
                    <Image src={feature.image} alt={feature.alt} width={560} height={350} />
                    {feature.className === "marketing-feature-card--sources" && (
                      <Image className="marketing-feature-scout" src="/brand/pocketorbit-scout.png" alt="" aria-hidden="true" width={284} height={362} />
                    )}
                  </div>
                  <div className="marketing-feature-copy"><h3>{feature.title}</h3><p>{feature.description}</p></div>
                </article>
              ))}
            </div>
          </ScrollReveal>
          <p className="marketing-illustration-note">Illustrations show the product direction. The current demo is a sample portfolio.</p>
        </section>

        <section className="marketing-activity-band" aria-labelledby="activity-title">
          <ScrollReveal className="marketing-activity-reveal">
            <div className="page-container marketing-activity-layout">
              <div className="marketing-activity-copy">
                <span className="marketing-section-kicker">Understand your activity</span>
                <h2 id="activity-title">Movement should make sense.</h2>
                <p>We are designing an activity view that makes transfers between your own wallets easier to recognize and keeps records needing review visible.</p>
                <Link className="text-link" href="/how-it-works">See the approach</Link>
              </div>
              <div className="marketing-activity-art">
                <Image src="/illustrations/activity-trail.svg" alt="Illustrative activity timeline with a matched internal transfer" width={640} height={420} />
                <Image className="marketing-activity-comet" src="/brand/pocketorbit-comet.png" alt="" aria-hidden="true" width={330} height={347} />
              </div>
            </div>
          </ScrollReveal>
        </section>

        <section aria-label="More ways PocketOrbit keeps things clear">
          <ScrollReveal className="page-container marketing-more marketing-more-reveal">
            <article>
              <span className="marketing-more-orbit marketing-more-orbit--sky" aria-hidden="true" />
              <h2>Made for a wider world.</h2>
              <p>Networks, currencies, and time zones matter when your holdings are spread across places. PocketOrbit is being designed with that context in mind.</p>
            </article>
            <article>
              <span className="marketing-more-orbit marketing-more-orbit--sun" aria-hidden="true" />
              <h2>Clear words, fewer guesses.</h2>
              <p>Short explanations help make balances, fees, and source labels easier to understand.</p>
              <Link className="text-link" href="/learn">Explore the glossary</Link>
            </article>
          </ScrollReveal>
        </section>

        <section className="page-container marketing-final-wrap">
          <ScrollReveal className="marketing-final-reveal">
            <div className="marketing-final-cta">
              <div><h2>See your crypto more clearly.</h2><p>Take a look at the sample portfolio. No account or wallet connection is needed.</p></div>
              <Link className="button button--primary" href="/app">Open the sample portfolio</Link>
            </div>
          </ScrollReveal>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
