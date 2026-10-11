import Image from "next/image";
import Link from "next/link";

import { ScrollReveal } from "@/components/scroll-reveal";
import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

const principles = [
  ["Keep your keys", "PocketOrbit will not ask for seed phrases, private keys, recovery words, or wallet signing access."],
  ["Keep control of your assets", "The product does not custody assets or execute trades, transfers, swaps, bridges, or withdrawals."],
  ["Check the information", "Balances and prices are intended to show their source and retrieval time. Partial or stale information should be labeled."],
  ["Know what is ready", "Email confirmation is disabled, so PocketOrbit does not confirm that an account email belongs to its user. Password reset needs configured email delivery. Sessions can be revoked, account actions are rate-limited, and portfolio access checks ownership."]
];

export default function SecurityPage() {
  return (
    <>
      <SiteHeader />
      <main className="page-container section-space detail-page">
        <ScrollReveal className="marketing-subpage-reveal">
          <section className="marketing-subpage-hero">
            <div className="marketing-subpage-copy">
              <span className="badge badge--success">Read-only by design</span>
              <h1 className="page-title">Your keys stay with you.</h1>
              <p className="body-copy">PocketOrbit is a portfolio companion built around public addresses and files you choose to import. It never needs the power to move your crypto.</p>
              <Link className="button button--secondary" href="/how-it-works">See how it works</Link>
            </div>
            <div className="marketing-subpage-art marketing-subpage-art--security">
              <Image src="/illustrations/read-only-orbit.svg" alt="Read-only shield with public address and file symbols" width={560} height={350} priority />
            </div>
          </section>
        </ScrollReveal>

        <ScrollReveal className="marketing-security-reveal">
          <div className="content-grid security-grid marketing-security-grid">
            {principles.map(([title, body]) => (
              <section className="panel content-panel" key={title}>
                <span className="security-mark" aria-hidden="true" />
                <h2>{title}</h2>
                <p>{body}</p>
              </section>
            ))}
          </div>
        </ScrollReveal>

        <ScrollReveal className="marketing-detail-note-reveal">
          <div className="detail-note"><strong>Production operations are still being completed.</strong><p>The sample portfolio uses illustrative values. Password recovery needs configured email delivery. Production also needs protected admin access, backups and restore drills, monitoring, retention rules, and reviewed legal policies.</p><Link className="text-link" href="/app">Explore the sample portfolio</Link></div>
        </ScrollReveal>
      </main>
      <SiteFooter />
    </>
  );
}
