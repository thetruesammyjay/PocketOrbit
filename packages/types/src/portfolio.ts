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
  totalValue: string | null;
  knownValue: string;
  change24h: string | null;
  changePercent24h: string | null;
  calculatedAt: string;
  quality: QualityStatus;
  warnings: string[];
  holdings: Holding[];
  sources: PortfolioSource[];
  allocation: AllocationItem[];
  activity: PortfolioActivity[];
  history: number[];
}
