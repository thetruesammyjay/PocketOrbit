import {
  Activity01Icon,
  BookOpen01Icon,
  ChartLineData01Icon,
  Clock01Icon,
  Database01Icon,
  Home01Icon,
  Logout01Icon,
  MoreHorizontalIcon,
  Settings01Icon,
  Upload01Icon,
  UserCircleIcon,
  Wallet01Icon,
  WalletAdd01Icon
} from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";

const icons = {
  home: Home01Icon,
  wallet: Wallet01Icon,
  activity: Activity01Icon,
  chart: ChartLineData01Icon,
  more: MoreHorizontalIcon,
  clock: Clock01Icon,
  database: Database01Icon,
  book: BookOpen01Icon,
  upload: Upload01Icon,
  walletAdd: WalletAdd01Icon,
  settings: Settings01Icon,
  logout: Logout01Icon,
  user: UserCircleIcon
};

export type IconName = keyof typeof icons;

export function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  return <HugeiconsIcon icon={icons[name]} size={size} strokeWidth={1.7} aria-hidden="true" />;
}
