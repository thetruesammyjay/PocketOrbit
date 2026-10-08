import Image from "next/image";
import Link from "next/link";

import { PortfolioPreview } from "@/components/portfolio-preview";
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

export default function HomePage() {
  return (
    <>
      <SiteHeader />
      <main className="marketing-home">
        <section className="marketing-hero">
          <div className="marketing-hero-scene marketing-hero-scene--left" aria-hidden="true">
            <Image src="/illustrations/orbit-scene-left.svg" alt="" width={520} height={620} priority />
            <Image className="marketing-hero-mascot" src="/brand/PocketOrbit-Orbit.png" alt="" width={1112} height={971} priority />
          </div>
          <div className="marketing-hero-copy page-container">
            <span className="marketing-hero-pill"><span aria-hidden="true" />The read-only portfolio companion</span>
            <h1>Your crypto, in one clear view.</h1>
            <p>Bring public wallets and exchange statements together. See what you own, where it is held, and where each number came from.</p>
            <div className="marketing-hero-actions">
              <Link className="button button--primary" href="/app">Explore the sample portfolio</Link>
              <Link className="button button--secondary" href="/how-it-works">See how it works</Link>
            </div>
            <span className="marketing-hero-note">No keys needed. The demo uses illustrative values.</span>
          </div>
          <div className="marketing-hero-scene marketing-hero-scene--right" aria-hidden="true">
            <Image src="/illustrations/orbit-scene-right.svg" alt="" width={520} height={620} priority />
          </div>
        </section>

        <section className="marketing-showcase" aria-labelledby="showcase-title">
          <div className="page-container marketing-section-heading">
            <div>
              <span className="marketing-section-kicker">A portfolio with context</span>
              <h2 id="showcase-title">Everything in orbit. Every detail in sight.</h2>
            </div>
            <p>A calm view of your holdings only helps when it also shows the source, freshness, and uncertainty behind the numbers.</p>
          </div>
          <div className="page-container"><PortfolioPreview /></div>
        </section>

        <section className="page-container marketing-features" id="features" aria-labelledby="features-title">
          <div className="marketing-section-heading marketing-section-heading--stacked">
            <span className="marketing-section-kicker">What makes the view clearer</span>
            <h2 id="features-title">The small details make a big difference.</h2>
          </div>
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
          <p className="marketing-illustration-note">Illustrations show the product direction. The current demo is a sample portfolio.</p>
        </section>

        <section className="marketing-activity-band" aria-labelledby="activity-title">
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
        </section>

        <section className="page-container marketing-more" aria-label="More ways PocketOrbit keeps things clear">
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
        </section>

        <section className="page-container marketing-final-wrap">
          <div className="marketing-final-cta">
            <div><h2>See your crypto more clearly.</h2><p>Take a look at the sample portfolio. No account or wallet connection is needed.</p></div>
            <Link className="button button--primary" href="/app">Open the sample portfolio</Link>
          </div>
        </section>
      </main>
      <SiteFooter />
    </>
  );
}
