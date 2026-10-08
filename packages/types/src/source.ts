export type QualityStatus =
  | "fresh"
  | "delayed"
  | "partial"
  | "needs_review"
  | "unmatched"
  | "offline"
  | "estimated";

export interface PortfolioSource {
  id: string;
  name: string;
  kind: "wallet" | "exchange_import" | "exchange_balance_import" | "exchange_api";
  network?: string | null;
  addressLabel?: string | null;
  lastUpdatedAt: string | null;
  quality: QualityStatus;
  coverage?: string | null;
  warnings?: string[];
}

export interface Provenance {
  sourceName: string;
  priceProvider?: string | null;
  retrievedAt: string;
  calculatedAt: string;
  quality: QualityStatus;
}
