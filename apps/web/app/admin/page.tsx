import { Badge, Card } from "@pocketorbit/ui";

import { PageHeading } from "@/components/page-heading";

export default function AdminOverviewPage() {
  return <><PageHeading title="Operations" description="Platform health and data quality overview." action={<Badge tone="warning">Placeholder</Badge>} /><div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Operations data is not available yet</strong>This page is restricted to configured administrator accounts, but it does not yet provide live user, import, source, or job monitoring. Use hosting and provider dashboards for operational monitoring.</div></div><div className="content-grid">{[["Users", "No admin service"], ["Imports", "No operations view"], ["Sources", "No provider monitor"], ["Jobs", "Background processing is not enabled"]].map(([name, value]) => <Card className="content-panel" key={name}><span className="eyebrow">{name}</span><h2 style={{ marginTop: "0.55rem" }}>{value}</h2><p>No live operations data is available.</p></Card>)}</div></>;
}
