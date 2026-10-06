import { Card } from "@pocketorbit/ui";

import type { AllocationItem } from "@pocketorbit/types";
import { formatCurrency } from "@/lib/format";

export function AllocationBreakdown({ items }: { items: AllocationItem[] }) {
  let cursor = 0;
  const stops = items.map((item) => {
    const start = cursor;
    cursor += item.percentage;
    return `${item.color} ${start}% ${cursor}%`;
  });

  return (
    <Card>
      <div className="panel-heading">
        <div><h2>Where it sits</h2><p>Sample allocation by asset</p></div>
      </div>
      <div className="allocation-body">
        <div className="allocation-ring" style={{ background: `conic-gradient(${stops.join(",")})` }} role="img" aria-label={`Allocation across ${items.length} sample assets`} />
        <div className="allocation-legend">
          {items.map((item) => (
            <div className="allocation-row" key={item.name}>
              <span className="allocation-dot" style={{ background: item.color }} />
              <strong>{item.name} <span className="muted">{item.percentage.toFixed(1)}%</span></strong>
              <span className="tabular">{formatCurrency(item.value)}</span>
            </div>
          ))}
        </div>
      </div>
    </Card>
  );
}
