import { Activity01Icon, ChartLineData01Icon, Clock01Icon, Home01Icon, MoreHorizontalIcon, Wallet01Icon } from "@hugeicons/core-free-icons";
import { HugeiconsIcon } from "@hugeicons/react";

const icons = {
  home: Home01Icon,
  wallet: Wallet01Icon,
  activity: Activity01Icon,
  chart: ChartLineData01Icon,
  more: MoreHorizontalIcon,
  clock: Clock01Icon
};

export type IconName = keyof typeof icons;

export function Icon({ name, size = 20 }: { name: IconName; size?: number }) {
  return <HugeiconsIcon icon={icons[name]} size={size} strokeWidth={1.7} aria-hidden="true" />;
}
