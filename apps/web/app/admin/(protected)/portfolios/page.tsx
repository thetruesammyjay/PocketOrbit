import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function PortfoliosPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Portfolios"
      description="Account portfolios and reporting preferences."
      endpoint="portfolios"
      columns={[
        { key: "name", label: "Portfolio" },
        { key: "ownerEmail", label: "Owner" },
        { key: "currency", label: "Currency" },
        { key: "createdAt", label: "Created" }
      ]}
    />
  );
}
