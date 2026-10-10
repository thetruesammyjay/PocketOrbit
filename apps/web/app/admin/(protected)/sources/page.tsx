import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function SourcesPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Data sources"
      description="Wallet and exchange balance source status."
      endpoint="sources"
      columns={[
        { key: "name", label: "Source" },
        { key: "ownerEmail", label: "Owner" },
        { key: "kind", label: "Type" },
        { key: "network", label: "Network" },
        { key: "address", label: "Address" },
        { key: "quality", label: "Quality" },
        { key: "lastUpdatedAt", label: "Last updated" }
      ]}
    />
  );
}
