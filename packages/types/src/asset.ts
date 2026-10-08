import type { QualityStatus } from "./source";

export interface Asset {
  id: string;
  symbol: string;
  name: string;
  network?: string | null;
  contractAddress?: string | null;
}
export interface Holding {
  asset: Asset;
  quantity: string;
  unitPrice: string | null;
  value: string | null;
  change24h?: string | null;
  sourceIds: string[];
  provenance?: {
    balanceSources: string[];
    balanceRetrievedAt: string | null;
    priceProvider: string | null;
    priceRetrievedAt: string | null;
    priceProviderUpdatedAt: string | null;
    quality: QualityStatus;
  };
}
