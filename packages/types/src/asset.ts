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
  unitPrice: string;
  value: string;
  change24h?: string | null;
  sourceIds: string[];
}
