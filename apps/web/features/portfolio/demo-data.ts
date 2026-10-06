import type { PortfolioSummary } from "@pocketorbit/types";

export const demoPortfolio: PortfolioSummary = {
  id: "demo-portfolio",
  name: "My portfolio",
  isDemo: true,
  reportingCurrency: "USD",
  totalValue: "31686.37",
  change24h: "352.01",
  changePercent24h: "1.12",
  calculatedAt: "sample",
  quality: "estimated",
  holdings: [
    { asset: { id: "bitcoin", symbol: "BTC", name: "Bitcoin" }, quantity: "0.084", unitPrice: "118500.00", value: "9954.00", change24h: "1.8", sourceIds: ["hardware-wallet", "exchange-import"] },
    { asset: { id: "ethereum", symbol: "ETH", name: "Ethereum", network: "Ethereum" }, quantity: "1.82", unitPrice: "3820.00", value: "6952.40", change24h: "0.9", sourceIds: ["exchange-import"] },
    { asset: { id: "solana", symbol: "SOL", name: "Solana", network: "Solana" }, quantity: "34.12", unitPrice: "186.40", value: "6359.97", change24h: "2.4", sourceIds: ["solana-wallet"] },
    { asset: { id: "usd-coin", symbol: "USDC", name: "USD Coin", network: "Ethereum" }, quantity: "8420", unitPrice: "1.00", value: "8420.00", change24h: "0.0", sourceIds: ["solana-wallet", "exchange-import"] }
  ],
  sources: [
    { id: "solana-wallet", name: "Everyday wallet", kind: "wallet", network: "Solana", addressLabel: "8F3…d72", lastUpdatedAt: "", quality: "estimated" },
    { id: "hardware-wallet", name: "Hardware wallet", kind: "wallet", network: "Bitcoin", addressLabel: "bc1…4xq", lastUpdatedAt: "", quality: "estimated" },
    { id: "exchange-import", name: "Exchange statement", kind: "exchange_import", addressLabel: "Sample CSV", lastUpdatedAt: "", quality: "estimated" }
  ],
  allocation: [
    { name: "BTC", value: "9954.00", percentage: 31.4, color: "#6C5CE7" },
    { name: "ETH", value: "6952.40", percentage: 21.9, color: "#56B7FF" },
    { name: "SOL", value: "6359.97", percentage: 20.1, color: "#18C98B" },
    { name: "USDC", value: "8420.00", percentage: 26.6, color: "#FFC857" }
  ],
  activity: [
    { id: "activity-1", kind: "received", assetSymbol: "USDC", quantity: "320.00", sourceName: "Everyday wallet", occurredAt: "Sample record", status: "confirmed" },
    { id: "activity-2", kind: "fee", assetSymbol: "SOL", quantity: "0.004", sourceName: "Everyday wallet", occurredAt: "Sample record", status: "confirmed" },
    { id: "activity-3", kind: "trade", assetSymbol: "ETH", quantity: "0.25", sourceName: "Exchange statement", occurredAt: "Sample record", status: "needs_review" }
  ],
  history: [29720, 30110, 29980, 30550, 30280, 31022, 31334, 31686.37]
};
