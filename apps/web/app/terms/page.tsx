import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function TermsPage() {
  return <><SiteHeader /><main className="page-container section-space detail-page"><span className="badge badge--violet">Terms</span><h1 className="page-title" style={{ marginTop: "1rem" }}>Terms of use</h1><div className="coming-soon"><div><strong>Terms are not finalized</strong><p>PocketOrbit is a read-only portfolio prototype, not a financial, investment, or tax adviser. Wallet coverage, prices, and imported history can be incomplete or delayed. Reviewed terms are required before public use; do not rely on this prototype for financial decisions.</p></div></div></main><SiteFooter /></>;
}
