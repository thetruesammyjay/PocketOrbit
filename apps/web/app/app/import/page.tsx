import { PageHeading } from "@/components/page-heading";
import { ImportPreviewForm } from "@/features/imports/import-preview-form";

export default function ImportPage() {
  return (
    <>
      <PageHeading title="Import an exchange file" description="Map an exchange CSV and save either transaction history or current account balances." />
      <div className="demo-banner">
        <span aria-hidden="true">i</span>
        <div><strong>Choose the kind of file</strong>Transaction history appears as activity. A current balance statement can populate holdings, but stays marked for review because PocketOrbit cannot independently verify an exchange file.</div>
      </div>
      <ImportPreviewForm />
    </>
  );
}
