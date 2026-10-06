import Image from "next/image";

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
        <section className="feature-intro learn-intro">
          <div>
            <span className="badge badge--violet">Learn</span>
            <h1 className="page-title">Crypto, in plain language.</h1>
            <p className="body-copy">Short explanations for terms you may see while reviewing a portfolio.</p>
          </div>
          <aside className="learn-guide">
            <Image src="/brand/pocketorbit-scout.png" alt="" aria-hidden="true" width={284} height={362} />
            <span>Clear words make details easier to follow.</span>
          </aside>
        </section>
        <dl className="glossary-list">
          {terms.map(([term, definition]) => (
            <div className="glossary-row" key={term}>
              <dt>{term}</dt><dd>{definition}</dd>
            </div>
          ))}
        </dl>
      </main>
      <SiteFooter />
    </>
  );
}
