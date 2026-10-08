import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function ImportsPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Imports"
      description="CSV import outcomes and row validation."
      endpoint="imports"
      columns={[
        { key: "filename", label: "File" },
        { key: "ownerEmail", label: "Owner" },
        { key: "status", label: "Status" },
        { key: "rowsAccepted", label: "Accepted" },
        { key: "rowsRejected", label: "Rejected" },
        { key: "createdAt", label: "Created" }
      ]}
    />
  );
}
