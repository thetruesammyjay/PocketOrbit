import { FeaturePage } from "@/components/feature-page";

export default function AppLearnPage() {
  return <FeaturePage title="Learn" description="Short explanations for portfolio and crypto terms." ><div className="content-grid"><article className="panel content-panel"><h2>Stablecoin</h2><p>A token designed to track another asset, often a currency. Its value can still vary.</p></article><article className="panel content-panel"><h2>Network fee</h2><p>A fee recorded for processing an action on a blockchain network.</p></article><article className="panel content-panel"><h2>Reporting currency</h2><p>The currency used to display portfolio values. It does not change native crypto quantities.</p></article><article className="panel content-panel"><h2>Unmatched record</h2><p>A record PocketOrbit cannot safely connect to an asset yet. Matching by symbol alone is not enough.</p></article></div></FeaturePage>;
}
