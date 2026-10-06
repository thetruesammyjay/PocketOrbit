import Image from "next/image";

import { PageHeading } from "@/components/page-heading";
import { ImportPreviewForm } from "@/features/imports/import-preview-form";

export default function ImportPage() {
  return (
    <>
      <PageHeading title="Import an exchange file" description="Preview a CSV before it becomes portfolio data." />
      <div className="demo-banner">
        <span aria-hidden="true">i</span>
        <div><strong>Preview only</strong>The scaffold can preview CSV columns and a few rows when the API is running. It does not yet normalize exchange formats or save records.</div>
      </div>
      <aside className="app-mascot-note import-mascot-note">
        <Image src="/brand/pocketorbit-comet.png" alt="" aria-hidden="true" width={330} height={347} />
        <p><strong>Start with an exchange export.</strong><span>This preview is temporary. It does not save or import records to your portfolio.</span></p>
      </aside>
      <ImportPreviewForm />
    </>
  );
}
