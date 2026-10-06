import { Badge } from "@pocketorbit/ui";

import type { QualityStatus } from "@pocketorbit/types";

const labels: Record<QualityStatus, string> = {
  fresh: "Fresh",
  delayed: "Delayed",
  partial: "Partial",
  needs_review: "Needs review",
  unmatched: "Unmatched",
  offline: "Offline",
  estimated: "Sample data"
};

const tones: Record<QualityStatus, "neutral" | "success" | "warning" | "danger" | "violet"> = {
  fresh: "success",
  delayed: "warning",
  partial: "warning",
  needs_review: "warning",
  unmatched: "danger",
  offline: "neutral",
  estimated: "warning"
};

export function QualityStatusBadge({ status }: { status: QualityStatus }) {
  return <Badge tone={tones[status]}>{labels[status]}</Badge>;
}
