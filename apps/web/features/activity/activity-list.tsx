import type { PortfolioActivity } from "@pocketorbit/types";

function activityLabel(kind: PortfolioActivity["kind"]) {
  const labels: Record<PortfolioActivity["kind"], string> = {
    received: "Received",
    sent: "Sent",
    trade: "Trade record",
    fee: "Network fee",
    deposit: "Deposit record",
    withdrawal: "Withdrawal record"
  };
  return labels[kind];
}

export function ActivityList({ items }: { items: PortfolioActivity[] }) {
  return (
    <div className="activity-list">
      {items.map((item) => (
        <div className="activity-row" key={item.id}>
          <span className="activity-mark" aria-hidden="true">{item.assetSymbol.slice(0, 2)}</span>
          <span className="activity-copy"><strong>{activityLabel(item.kind)} {item.assetSymbol}</strong><span>{item.sourceName} · {item.occurredAt}</span></span>
          <span className="activity-amount">{item.quantity} {item.assetSymbol}</span>
        </div>
      ))}
    </div>
  );
}
