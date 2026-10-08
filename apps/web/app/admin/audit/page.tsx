import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function AuditPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Audit log"
      description="Admin page access events persisted in the application database."
      endpoint="audit"
      columns={[
        { key: "actorEmail", label: "Administrator" },
        { key: "action", label: "Action" },
        { key: "targetType", label: "Target type" },
        { key: "targetId", label: "Target" },
        { key: "createdAt", label: "Time" }
      ]}
    />
  );
}
