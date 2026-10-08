import { AdminDataPage } from "@/components/admin-data-page";

export default function SystemPage() {
  return (
    <AdminDataPage
      title="System health"
      description="Database, schema, email, and provider configuration checks."
      endpoint="system"
      collection="checks"
      columns={[
        { key: "name", label: "Check" },
        { key: "status", label: "Status" },
        { key: "details", label: "Details" }
      ]}
    />
  );
}
