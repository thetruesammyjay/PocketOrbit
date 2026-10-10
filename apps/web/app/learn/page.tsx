import Image from "next/image";
import Link from "next/link";

import { ScrollReveal } from "@/components/scroll-reveal";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const terms = [
  ["Wallet", "An app or device that helps you manage crypto. A public wallet address can show activity, but it cannot authorize a transfer by itself."],
  ["Exchange statement", "A file exported from a crypto exchange. It can contain balances, deposits, withdrawals, fees, or trade records."],
  ["Stablecoin", "A crypto token designed to track the value of another asset, often a currency. Its value can still vary."],
  ["Network fee", "A fee recorded for processing an action on a blockchain network."],
  ["Source and freshness", "Where a balance or price came from and when the information was retrieved."]
];

export default function LearnPage() {
  return (
    <>
      <SiteHeader />
      <main className="page-container section-space detail-page">
        <ScrollReveal className="marketing-subpage-reveal">
          <section className="marketing-subpage-hero">
            <div className="marketing-subpage-copy">
              <span className="badge badge--violet">Learn</span>
              <h1 className="page-title">Crypto, in plain language.</h1>
              <p className="body-copy">A quick guide to the words you may see while reviewing a portfolio. Clear labels make details easier to follow.</p>
              <Link className="button button--secondary" href="/app/sources">See sample sources</Link>
            </div>
            <div className="marketing-subpage-art marketing-subpage-art--learn">
              <Image src="/illustrations/number-receipt.svg" alt="Illustrative value with its source, update, and quality details" width={560} height={350} priority />
              <Image className="marketing-subpage-mascot" src="/brand/pocketorbit-scout.png" alt="" aria-hidden="true" width={284} height={362} />
            </div>
          </section>
        </ScrollReveal>

        <ScrollReveal className="marketing-glossary-reveal">
          <dl className="glossary-list marketing-glossary-list">
            {terms.map(([term, definition]) => (
              <div className="glossary-row" key={term}>
                <dt>{term}</dt><dd>{definition}</dd>
              </div>
            ))}
          </dl>
        </ScrollReveal>
      </main>
      <SiteFooter />
    </>
  );
}
