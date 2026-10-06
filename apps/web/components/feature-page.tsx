import { Badge } from "@pocketorbit/ui";
import type { ReactNode } from "react";

import { PageHeading } from "@/components/page-heading";

export function FeaturePage({ title, description, children }: { title: string; description: string; children?: ReactNode }) {
  return (
    <>
      <PageHeading title={title} description={description} />
      {children ?? (
        <section className="coming-soon" aria-label={`${title} setup status`}>
          <Badge tone="warning">Scaffolded</Badge>
          <div>
            <strong>This page is ready for its next feature.</strong>
            <p>The route and shared layout are in place. Connect real portfolio services before treating this page as account data.</p>
          </div>
        </section>
      )}
    </>
  );
}
