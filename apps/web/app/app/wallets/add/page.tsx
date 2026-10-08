import { PageHeading } from "@/components/page-heading";
import { AddWalletForm } from "@/features/wallets/add-wallet-form";

export default function AddWalletPage() {
  return <><PageHeading title="Add a public wallet" description="Connect a public address to read balances and save a timestamped snapshot." /><AddWalletForm /></>;
}
