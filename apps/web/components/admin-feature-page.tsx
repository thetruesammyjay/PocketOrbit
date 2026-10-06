import { Badge, Card } from "@pocketorbit/ui";

import { PageHeading } from "@/components/page-heading";

export function AdminFeaturePage({ title, description }: { title: string; description: string }) {
  return <><PageHeading title={title} description={description} /><Card className="content-panel"><Badge tone="warning">Not connected</Badge><h2 style={{ marginTop: "1rem" }}>Operational data is not configured.</h2><p>Authentication, database access, and admin services must be added before this page can show or change production data.</p></Card></>;
}
