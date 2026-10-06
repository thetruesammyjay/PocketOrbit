import type { QualityStatus } from "./source";

export type WalletNetworkId = "solana" | "ethereum" | "base" | "arbitrum";

export interface WalletSyncRequest {
  network: WalletNetworkId;
  address: string;
  quoteCurrency?: string;
}

export interface BalanceProvenance {
  sourceName: string;
  sourceRecordIds: string[];
  retrievedAt: string;
  blockReference: string | null;
}

export interface PriceProvenance {
  sourceName: string;
  retrievedAt: string;
  providerUpdatedAt: string | null;
  quality: QualityStatus;
}

export interface LiveWalletBalance {
  assetId: string;
  symbol: string;
  name: string;
  network: WalletNetworkId;
  contractAddress: string | null;
  quantity: string;
  quoteCurrency: string;
  unitPrice: string | null;
  value: string | null;
  quality: QualityStatus;
  balanceProvenance: BalanceProvenance;
  priceProvenance: PriceProvenance | null;
}

export interface WalletSyncResponse {
  network: WalletNetworkId;
  networkName: string;
  coverage:
    | "native_and_spl_token2022_fungible_balances"
    | "native_and_configured_erc20_balances";
  address: string;
  isLive: true;
  isPersisted: false;
  retrievedAt: string;
  quoteCurrency: string;
  totalValue: string | null;
  knownValue: string;
  quality: QualityStatus;
  balances: LiveWalletBalance[];
  warnings: string[];
}

export interface WalletNetworkCapability {
  id: WalletNetworkId;
  name: string;
  configured: boolean;
  coverage: string;
  configuredTokenContracts?: number;
  invalidTokenContractEntries?: number;
  tokenContractsTruncated?: boolean;
}

export interface WalletCapabilitiesResponse {
  priceProvider: {
    name: string;
    configured: boolean;
  };
  networks: WalletNetworkCapability[];
  persistence: false;
  message: string;
}
