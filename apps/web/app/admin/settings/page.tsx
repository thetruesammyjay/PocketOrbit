import { AdminDataPage } from "@/components/admin-data-page";

export default function SettingsPage() {
  return (
    <AdminDataPage
      title="Admin settings"
      description="Safe configuration status; secret values are never returned."
      endpoint="settings"
      columns={[
        { key: "name", label: "Setting" },
        { key: "value", label: "Current value" },
        { key: "configured", label: "Configured" }
      ]}
    />
  );
}
