import Link from "next/link";

import { PageHeading } from "@/components/page-heading";

export default function AddWalletPage() {
  return <><PageHeading title="Add a public wallet" description="A public address can be used to read supported balances and activity." /><section className="panel content-panel"><span className="badge badge--warning">Provider not configured</span><div className="form-field"><label htmlFor="network">Network</label><select id="network" disabled defaultValue=""><option value="">No networks available</option></select></div><div className="form-field"><label htmlFor="wallet-address">Public address</label><input id="wallet-address" type="text" disabled placeholder="Wallet connection will be available later" /></div><p className="form-help">Never enter a seed phrase or private key. This scaffold does not connect to blockchain providers.</p><button className="button button--primary" disabled type="button">Wallet sync is unavailable</button><p><Link href="/app/sources">View sample sources</Link></p></section></>;
}
