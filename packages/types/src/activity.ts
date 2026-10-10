export type ActivityKind = "received" | "sent" | "trade" | "fee" | "deposit" | "withdrawal";

export interface PortfolioActivity {
  id: string;
  kind: ActivityKind;
  assetSymbol: string;
  quantity: string;
  sourceName: string;
  occurredAt: string;
  status: "confirmed" | "pending" | "needs_review" | "user_confirmed" | "rejected";
  transactionHash?: string | null;
  externalRecordId?: string | null;
  quoteAmount?: string | null;
  quoteCurrency?: string | null;
  transferStatus?: "suggested" | "matched" | "rejected" | null;
}
