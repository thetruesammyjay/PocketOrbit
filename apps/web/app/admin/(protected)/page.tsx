import { Card } from "@pocketorbit/ui";

import {
  AdminDataTable,
  fetchAdminData,
  formatAdminValue,
  type AdminRow
} from "@/components/admin-data-page";
import { PageHeading } from "@/components/page-heading";

export default async function AdminOverviewPage() {
  const data = await fetchAdminData("overview");
  const counts = (data.counts ?? {}) as Record<string, unknown>;
  const recentEvents = Array.isArray(data.recentEvents) ? data.recentEvents as AdminRow[] : [];
  const metrics = [
    ["Users", counts.users],
    ["Portfolios", counts.portfolios],
    ["Sources", counts.sources],
    ["Imports", counts.imports],
    ["Assets", counts.assets],
    ["Transactions", counts.transactions],
    ["Failed syncs", counts.failedSyncs]
  ] as const;

  return <>
    <PageHeading title="Operations" description="Live counts and recent administrator activity." />
    <div className="content-grid admin-metrics">
      {metrics.map(([name, value]) => <Card className="content-panel" key={name}>
        <span className="eyebrow">{name}</span>
        <h2 className="admin-metric-value">{formatAdminValue(value)}</h2>
      </Card>)}
    </div>
    <Card className="content-panel admin-audit-preview">
      <div className="panel-heading">
        <div>
          <h2>Recent admin access</h2>
          <p>Page views are recorded in the database audit table.</p>
        </div>
      </div>
      <AdminDataTable rows={recentEvents} columns={[
        { key: "actorEmail", label: "Administrator" },
        { key: "action", label: "Action" },
        { key: "createdAt", label: "Time" }
      ]} />
    </Card>
  </>;
}
