import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function TermsPage() {
  return <><SiteHeader /><main className="page-container section-space detail-page"><span className="badge badge--violet">Terms</span><h1 className="page-title" style={{ marginTop: "1rem" }}>Terms of use</h1><div className="coming-soon"><div><strong>Draft page</strong><p>Reviewed terms are required before this scaffold is used as a public service.</p></div></div></main><SiteFooter /></>;
}
