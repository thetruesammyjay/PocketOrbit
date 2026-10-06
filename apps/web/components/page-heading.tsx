import type { ReactNode } from "react";

export function PageHeading({ title, description, action }: { title: string; description?: string; action?: ReactNode }) {
  return (
    <div className="dashboard-heading">
      <div>
        <h1 className="page-title">{title}</h1>
        {description && <p>{description}</p>}
      </div>
      {action}
    </div>
  );
}
