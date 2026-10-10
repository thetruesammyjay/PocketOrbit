import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function AssetsPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Asset registry"
      description="Canonical asset identities used for portfolio matching."
      endpoint="assets"
      columns={[
        { key: "symbol", label: "Symbol" },
        { key: "name", label: "Name" },
        { key: "network", label: "Network" },
        { key: "contract", label: "Contract / mint" },
        { key: "decimals", label: "Decimals" },
        { key: "canonicalId", label: "Canonical ID" }
      ]}
    />
  );
}
