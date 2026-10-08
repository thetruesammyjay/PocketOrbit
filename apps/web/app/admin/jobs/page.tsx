import {
  AdminDataPage,
  resolveAdminOffset,
  type AdminRouteProps
} from "@/components/admin-data-page";

export default async function JobsPage({ searchParams }: AdminRouteProps) {
  const offset = await resolveAdminOffset(searchParams);
  return (
    <AdminDataPage
      offset={offset}
      title="Jobs"
      description="Wallet refreshes and CSV import processing."
      endpoint="jobs"
      columns={[
        { key: "jobType", label: "Job" },
        { key: "status", label: "Status" },
        { key: "source", label: "Source" },
        { key: "ownerEmail", label: "Owner" },
        { key: "message", label: "Result" },
        { key: "createdAt", label: "Started" }
      ]}
    />
  );
}
