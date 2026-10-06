import { Badge, Card } from "@pocketorbit/ui";

import { PageHeading } from "@/components/page-heading";

export default function AdminOverviewPage() {
  return <><PageHeading title="Operations" description="Platform health and data quality overview." action={<Badge tone="warning">Scaffold only</Badge>} /><div className="demo-banner"><span aria-hidden="true">i</span><div><strong>Admin access is not protected yet</strong>This interface contains no live operational data. Do not connect production accounts until authentication and authorization are implemented.</div></div><div className="content-grid">{[["Users", "Waiting for authentication"], ["Imports", "No import jobs stored"], ["Sources", "Provider checks are not configured"], ["Jobs", "Background processing is not enabled"]].map(([name, value]) => <Card className="content-panel" key={name}><span className="eyebrow">{name}</span><h2 style={{ marginTop: "0.55rem" }}>{value}</h2><p>No production records are available in this scaffold.</p></Card>)}</div></>;
}
