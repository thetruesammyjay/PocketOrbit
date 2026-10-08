import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function PrivacyPage() {
  return <><SiteHeader /><main className="page-container section-space detail-page"><span className="badge badge--violet">Privacy</span><h1 className="page-title" style={{ marginTop: "1rem" }}>Privacy information</h1><div className="coming-soon"><div><strong>Privacy policy draft</strong><p>PocketOrbit stores your email, password hash, session record, portfolio, connected public wallet addresses and snapshots, imported transaction rows, and price history. CSV uploads are processed and discarded; normalized records and a file fingerprint are retained. Public wallet and price requests are sent to configured providers. PocketOrbit never asks for seed phrases or private keys. You can remove active account data from Settings.</p><p>This implementation notice is not a reviewed privacy policy. Backup retention, provider terms, and your legal rights need review before public launch. Backup copies may remain until their retention policy expires.</p></div></div></main><SiteFooter /></>;
}
