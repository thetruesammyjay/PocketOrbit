export type ActivityKind = "received" | "sent" | "trade" | "fee" | "deposit" | "withdrawal";

export interface PortfolioActivity {
  id: string;
  kind: ActivityKind;
  assetSymbol: string;
  quantity: string;
  sourceName: string;
  occurredAt: string;
  status: "confirmed" | "pending" | "needs_review";
}
