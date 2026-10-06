import type { Holding } from "./asset";
import type { PortfolioActivity } from "./activity";
import type { PortfolioSource, QualityStatus } from "./source";

export interface AllocationItem {
  name: string;
  value: string;
  percentage: number;
  color: string;
}

export interface PortfolioSummary {
  id: string;
  name: string;
  isDemo: boolean;
  reportingCurrency: string;
  totalValue: string;
  change24h: string;
  changePercent24h: string;
  calculatedAt: string;
  quality: QualityStatus;
  holdings: Holding[];
  sources: PortfolioSource[];
  allocation: AllocationItem[];
  activity: PortfolioActivity[];
  history: number[];
}
