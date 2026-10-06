import { SiteFooter } from "@/components/site-footer";
import { SiteHeader } from "@/components/site-header";

export default function PrivacyPage() {
  return <><SiteHeader /><main className="page-container section-space detail-page"><span className="badge badge--violet">Privacy</span><h1 className="page-title" style={{ marginTop: "1rem" }}>Privacy information</h1><div className="coming-soon"><div><strong>Draft page</strong><p>This scaffold does not yet collect or store account data. A reviewed privacy policy must be added before production accounts or provider connections are enabled.</p></div></div></main><SiteFooter /></>;
}
